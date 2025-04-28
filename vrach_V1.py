from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real
from datetime import datetime

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'

    minimal_roi = {
        "0": 0.05,
        "60": 0.03,
        "120": 0.01
    }

    stoploss = -0.02

    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    use_custom_stoploss = True
    use_custom_exit = True

    can_short = False
    process_only_new_candles = True

    @staticmethod
    def hyperopt_parameters():
        return {
            'minimal_roi': {
                '0': Real(0.02, 0.06),
                '60': Real(0.01, 0.04),
                '120': Real(0.005, 0.02),
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
        # Samo u slučaju velikog RSI
        dataframe.loc[
            (dataframe['rsi'] > 80),
            'exit_long'
        ] = 1
        return dataframe

    @property
    def market_crash(self) -> bool:
        btc_df = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe="5m")
        if btc_df is not None and len(btc_df) > 5:
            last_close = btc_df['close'].iloc[-1]
            prev_close = btc_df['close'].iloc[-5]
            change = (last_close - prev_close) / prev_close
            if change < -0.05:  # BTC padne više od 5% na 5 sveća (~25min)
                return True
        return False

    def custom_stoploss(self, pair: str, trade, current_time: datetime, current_rate: float,
                        current_profit: float, **kwargs):
        """
        Dinamički stoploss baziran na kretanju tržišta + panic exit ako treba
        """
        # Panic sell ako market crash
        if self.market_crash:
            return -0.001  # praktično odmah prodaj

        # Dinamički stoploss
        # Ako smo u profitu više, jače stežemo stop
        if current_profit > 0.05:
            return -0.01  # 1% max gubitak
        elif current_profit > 0.03:
            return -0.015
        elif current_profit > 0.01:
            return -0.02
        else:
            return -0.03  # početni veći stop dok trade ne ode

    def custom_exit(self, pair: str, trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
        """
        Custom izlaz baziran na profitu i situaciji na tržištu
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or len(dataframe) < 1:
            return None

        last_candle = dataframe.iloc[-1]

        # Panic sell
        if self.market_crash:
            return 'panic_exit'

        # Ako imamo lep profit zatvaramo
        if current_profit > 0.06:
            return 'take_profit'

        # Ako RSI krene da pada i imamo dobit zatvaramo
        if last_candle['rsi'] > 70 and current_profit > 0.02:
            return 'rsi_exit'

        return None
