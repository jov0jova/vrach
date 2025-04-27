from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class Vrach_Ultimate_PRO_2(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'
    inf_timeframe = '1h'  # koristimo i dodatni timeframe za bolji kontekst

    minimal_roi = {
        "0": 0.03,   # Povećano jer ulazi sigurnije
        "10": 0.015,
        "30": 0
    }

    stoploss = -0.02

    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    use_custom_stoploss = False

    can_short = False

    process_only_new_candles = True
    startup_candle_count: int = 300

    def informative_pairs(self):
        return [("BTC/USDT", self.inf_timeframe)]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMA
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)

        # Volume
        dataframe['volume_mean_slow'] = dataframe['volume'].rolling(window=50).mean()

        # Wick and body
        dataframe['upper_wick'] = dataframe['high'] - dataframe[['close', 'open']].max(axis=1)
        dataframe['lower_wick'] = dataframe[['close', 'open']].min(axis=1) - dataframe['low']
        dataframe['body'] = abs(dataframe['close'] - dataframe['open'])

        # Informative timeframe indicators (1h BTC/USDT market crash detection)
        inf_df = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe=self.inf_timeframe)
        if inf_df is not None:
            inf_df['rsi_btc'] = ta.RSI(inf_df, timeperiod=14)
            self.btc_rsi = inf_df['rsi_btc'].iloc[-1]
            self.btc_pct_change = (inf_df['close'].iloc[-1] - inf_df['close'].iloc[-6]) / inf_df['close'].iloc[-6]

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
            (dataframe['volume'] > dataframe['volume_mean_slow'] * 2) &
            (dataframe['close'] > dataframe['ema50'])
        )

        trend_reversal_signal = (
            (dataframe['ema50'] > dataframe['ema200']) &
            (dataframe['rsi_fast'] < 40) &
            (dataframe['lower_wick'] > dataframe['body'])
        )

        # Kombinovani entry
        dataframe.loc[
            (
                (hammer_signal | scalping_signal | trend_reversal_signal) &
                (~self.market_crash) &
                (self.btc_rsi > 35)
            ),
            'enter_long'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['ema50']) &
                (dataframe['rsi'] > 60)
            ),
            'exit_long'
        ] = 1
        return dataframe

    @property
    def market_crash(self) -> bool:
        try:
            return self.btc_pct_change < -0.02
        except AttributeError:
            return False
