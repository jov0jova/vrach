from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real
import numpy as np

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'

    minimal_roi = {
        "0": 0.02,
        "10": 0.01,
        "20": 0
    }

    stoploss = -0.015

    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    use_custom_stoploss = True
    can_short = False
    process_only_new_candles = True

    @staticmethod
    def hyperopt_parameters():
        return {
            'minimal_roi': {
                '0': Real(0.01, 0.05),
                '10': Real(0.005, 0.03),
                '20': Real(0, 0.02),
            },
            'stoploss': Real(-0.05, -0.01),
            'trailing_stop': Categorical([True, False]),
            'trailing_stop_positive': Real(0.005, 0.08),
            'trailing_stop_positive_offset': Real(0.01, 0.08),
            'exit_rsi_threshold': Real(65, 85),
            'atr_multiplier_sl': Real(1.0, 3.0),
            'atr_multiplier_tp': Real(2.0, 5.0),
        }

    def informative_pairs(self):
        return [("BTC/USDT", "5m")]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['ema9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        atr_rolling_avg = dataframe['atr'].rolling(window=50).mean()
        dataframe['is_high_volatility'] = dataframe['atr'] > atr_rolling_avg * 1.5
        dataframe['volume_mean_slow'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['upper_wick'] = dataframe['high'] - dataframe[['close', 'open']].max(axis=1)
        dataframe['lower_wick'] = dataframe[['close', 'open']].min(axis=1) - dataframe['low']
        dataframe['body'] = abs(dataframe['close'] - dataframe['open'])
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        hammer_signal = (
            (dataframe['close'] < dataframe['ema200']) &
            (dataframe['rsi'] < 35) &
            (dataframe['volume'] > dataframe['volume_mean_slow'] * 1.5) &
            (dataframe['lower_wick'] > dataframe['body'] * 1.5)
        )

        scalping_signal = (
            (dataframe['rsi_fast'] < 30) &
            (dataframe['volume'] > dataframe['volume_mean_slow'] * 2)
        )

        dataframe.loc[
            (hammer_signal | scalping_signal) & (~self.market_crash),
            'enter_long'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['close'] > dataframe['ema50']) |
            (dataframe['rsi'] > self.dp.runmode.get('exit_rsi_threshold', 75)),
            'exit_long'
        ] = 1
        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float, current_profit: float, **kwargs) -> float:
        dataframe, _ = self.dp.get_pair_dataframe(pair=pair, timeframe=self.timeframe)
        if dataframe is not None and not dataframe.empty:
            last_atr = dataframe['atr'].iloc[-1]
            return current_rate - (last_atr * self.dp.runmode.get('atr_multiplier_sl', 2.0))
        return -0.05 # Fallback stoploss if ATR is not available

    def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float, current_profit: float, **kwargs):
        dataframe, _ = self.dp.get_pair_dataframe(pair=pair, timeframe=self.timeframe)
        if dataframe is not None and not dataframe.empty:
            last_atr = dataframe['atr'].iloc[-1]
            take_profit_level = trade.open_rate + (last_atr * self.dp.runmode.get('atr_multiplier_tp', 3.0))
            if current_rate >= take_profit_level:
                return 'atr_take_profit'
        return None

    @property
    def market_crash(self) -> bool:
        btc_df = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe="5m")
        if btc_df is not None and len(btc_df) > 5:
            last_close = btc_df['close'].iloc[-1]
            prev_close = btc_df['close'].iloc[-5]
            change = (last_close - prev_close) / prev_close
            if change < -0.02:
                return True
        return False

    def dynamic_roi(self) -> dict:
        dataframe, _ = self.dp.get_pair_dataframe(pair=self.config['stake_currency'] + '/USDT', timeframe=self.timeframe)
        if dataframe is not None and not dataframe.empty:
            last_atr = dataframe['atr'].iloc[-1]
            # Adjust ROI based on ATR. Higher volatility (higher ATR) might allow for higher ROI targets.
            return {
                "0": min(0.02 + (last_atr * 10), 0.08),  # Example: Base ROI + ATR factor
                "10": min(0.01 + (last_atr * 7.5), 0.05),
                "20": min(0.00 + (last_atr * 5), 0.03),
                "60": 0 # Add a longer timeframe ROI as a fallback
            }
        return self.minimal_roi # Fallback to static ROI if ATR is not available

    def get_minimal_roi(self, current_profit: float, current_time: 'datetime') -> dict:
        return self.dynamic_roi()
