from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class Vrach_Ultimate_REALTIME(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'  # Koristimo 5-minutni interval

    minimal_roi = {
        "0": 0.05,
        "10": 0.03,
        "20": 0.02
    }

    stoploss = -0.05
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = True

    use_custom_stoploss = False
    can_short = False
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)
        dataframe['volume_mean_slow'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['upper_wick'] = dataframe['high'] - dataframe[['close', 'open']].max(axis=1)
        dataframe['lower_wick'] = dataframe[['close', 'open']].min(axis=1) - dataframe['low']
        dataframe['body'] = abs(dataframe['close'] - dataframe['open'])
        
        # Analiza poslednjih 24 sveća
        self._identify_peak_candle(dataframe)
        
        return dataframe

    def _identify_peak_candle(self, dataframe: DataFrame):
        # Gledamo poslednjih 24 sveće na 5m time frame-u
        recent_candles = dataframe.tail(24)  # koristimo tail da bismo uzeli poslednjih 24 reda

        # Na osnovu maksimalnog zatvaranja pronalazimo "peak" sveću
        peak_candle = recent_candles.loc[recent_candles['close'].idxmax()]
        
        # Spremamo parametre "peak" sveće
        self.peak_rsi = peak_candle['rsi']
        self.peak_ema50 = peak_candle['ema50']
        self.peak_ema200 = peak_candle['ema200']

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
            (hammer_signal | scalping_signal),
            'enter_long'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if hasattr(self, 'peak_rsi'):
            # Upoređujemo trenutni RSI i EMA sa "peak" svećama
            rsi_threshold = self.peak_rsi * 0.90
            ema50_threshold = self.peak_ema50 * 0.90
            ema200_threshold = self.peak_ema200 * 0.90

            # Izlazimo ako je trenutni RSI i EMA iznad 90% peak vrednosti
            dataframe.loc[
                (dataframe['rsi'] > rsi_threshold) & 
                (dataframe['ema50'] > ema50_threshold) & 
                (dataframe['close'] > ema50_threshold),
                'exit_long'
            ] = 1

        return dataframe
