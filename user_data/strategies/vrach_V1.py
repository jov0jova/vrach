from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class vrach_V1(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'
    informative_timeframes = {
        '30m': ['close', 'ema50', 'ema200', 'rsi'],
        '1h': ['close', 'ema50', 'ema200', 'rsi'],
        '1d': ['close', 'ema50', 'ema200', 'rsi']
    }
    startup_candle_count = 150

    minimal_roi = {"0": 0.02}  # 2% target
    stoploss = -0.02
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015

    use_custom_stoploss = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['momentum'] = dataframe['close'] - dataframe['close'].shift(5)
        dataframe['volume_mean'] = dataframe['volume'].rolling(30).mean()
        dataframe['percent_change'] = dataframe['close'].pct_change() * 100

        # Novi indikatori
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        stoch = ta.STOCHRSI(dataframe, timeperiod=14)
        dataframe['stochrsi_k'] = stoch['fastk']
        dataframe['stochrsi_d'] = stoch['fastd']

        # EMA50 slope
        dataframe['ema50_slope'] = dataframe['ema50'] - dataframe['ema50'].shift(1)

        return dataframe

def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            (dataframe['ema50'] > dataframe['ema200']) &  # EMA50 veća od EMA200 (bullish trend)
            (dataframe['ema50_slope'] > 0) &  # EMA50 raste
            (dataframe['rsi'] > 35) & (dataframe['rsi'] < 65) &  # RSI u normalnom opsegu
            (dataframe['percent_change'] < -0.5) & (dataframe['percent_change'] > -3.0) &  # Promena cena u poslednjih nekoliko perioda
            (dataframe['momentum'] > 0) &  # Pozitivan momentum
            (dataframe['macd'] > dataframe['macdsignal']) &  # MACD linija je iznad signalne linije
            (dataframe['macdhist'] > 0) &  # MACD histogram je pozitivan
            (dataframe['stochrsi_k'] < 20) & (dataframe['stochrsi_d'] < 20) &  # StochRSI je u oversold zoni
            (dataframe['volume'] > dataframe['volume_mean'] * 0.7)  # Volumen veći od prosečnog
        ),
        'buy'
    ] = 1  # Postavi signal za kupovinu kada su svi uslovi ispunjeni
    return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |
                (dataframe['close'] < dataframe['ema50']) |
                (dataframe['momentum'] < 0)  # Momentum opada
            ),
            'sell'
        ] = 1
        return dataframe

    def custom_stoploss(self, pair: str, trade, current_time, current_rate, current_profit, **kwargs):
        if current_profit > 0.015:
            return -0.005
        return self.stoploss
