from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'

    minimal_roi = {
        "0": 0.03,
        "10": 0.015,
        "20": 0.005
    }

    stoploss = -0.05

    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    use_custom_stoploss = False
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
            'trailing_stop_positive': Real(0.005, 0.04),
            'trailing_stop_positive_offset': Real(0.01, 0.05),
        }

    def informative_pairs(self):
        return [("BTC/USDT", "5m")]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)
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
        # Initialize peak tracking
        dataframe['peak_price'] = dataframe['close'].cummax()
        dataframe['peak_rsi'] = dataframe['rsi'].cummax()

        # Define exit conditions based on peak tracking
        dataframe.loc[
            (dataframe['close'] < dataframe['peak_price'] * 0.95) |
            (dataframe['rsi'] < dataframe['peak_rsi'] * 0.90),
            'exit_long'] = 1

        return dataframe

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
		
		
		
		
