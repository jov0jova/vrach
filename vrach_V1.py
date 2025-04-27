from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class vrach_V1(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'
    informative_timeframes = {
        '5m': ['close', 'ema50', 'ema200', 'rsi'],
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
    
        # Konverzija u numeričke vrednosti
        for column in ['close', 'ema50', 'ema200', 'rsi', 'atr', 'momentum', 'percent_change']:
            dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
    
        # Uklanjanje NaN vrednosti
        dataframe.dropna(inplace=True)
    
        # Bollinger Bands
        dataframe['bb_lower'], dataframe['bb_middle'], dataframe['bb_upper'] = ta.BBANDS(dataframe, timeperiod=20)
    
        # StochRSI
        stoch = ta.STOCHRSI(dataframe, timeperiod=14)
        dataframe['stochrsi_k'] = stoch['fastk']
        dataframe['stochrsi_d'] = stoch['fastd']
    
        # EMA50 slope
        dataframe['ema50_slope'] = dataframe['ema50'] - dataframe['ema50'].shift(1)
    
        return dataframe

    
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema50'] > dataframe['ema200']) &  # Bullish trend
                (dataframe['ema50_slope'] > 0) &  # EMA50 raste
                (dataframe['rsi'] > 35) & (dataframe['rsi'] < 65) &  # RSI u neutralnom opsegu
                (dataframe['momentum'] > 0) &  # Pozitivan momentum
                (dataframe['close'] < dataframe['bb_lower']) &  # Cena dodiruje donju Bollinger Band granicu
                (dataframe['stochrsi_k'] < 20) & (dataframe['stochrsi_d'] < 20)  # StochRSI oversold zona
            ),
            'buy'
        ] = 1
        return dataframe
    
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |  # RSI overbought zona
                (dataframe['momentum'] < 0) |  # Momentum opada
                (dataframe['close'] > dataframe['bb_upper']) |  # Cena dodiruje gornju Bollinger Band granicu
                ((dataframe['close'] < dataframe['ema50']) & (dataframe['ema50_slope'] < 0))  # Cena ispod EMA50
            ),
            'sell'
        ] = 1
        return dataframe

    def custom_stoploss(self, pair: str, trade, current_time, current_rate, current_profit, **kwargs):
        if current_profit > 0.015:
            return -0.005
        return self.stoploss
