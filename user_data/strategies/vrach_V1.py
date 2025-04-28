from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real
from datetime import datetime
from freqtrade.persistence import Trade

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'

    # Optimizacija parametara
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
    use_custom_stoploss = True  # Aktiviramo custom stoploss

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
        # EMA i RSI indikatori
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)
        
        # Volume analiza
        dataframe['volume_mean_slow'] = dataframe['volume'].rolling(window=20).mean()
        
        # Sveća analiza
        dataframe['upper_wick'] = dataframe['high'] - dataframe[['close', 'open']].max(axis=1)
        dataframe['lower_wick'] = dataframe[['close', 'open']].min(axis=1) - dataframe['low']
        dataframe['body'] = abs(dataframe['close'] - dataframe['open'])
        
        # Trend snaga
        dataframe['trend_strength'] = ((dataframe['close'] - dataframe['close'].rolling(50).mean()) / 
                                      dataframe['close'].rolling(50).std())
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Hammer signal sa dodatnim filterima
        hammer_signal = (
            (dataframe['close'] < dataframe['ema200']) &
            (dataframe['rsi'] < 35) &
            (dataframe['volume'] > dataframe['volume_mean_slow'] * 1.5) &
            (dataframe['lower_wick'] > dataframe['body'] * 1.5) &
            (dataframe['close'] > dataframe['open']) &  # Potvrda rasta
            (dataframe['trend_strength'] > -0.5)  # Trend filter
        )

        # Scalping signal sa dodatnim uslovima
        scalping_signal = (
            (dataframe['rsi_fast'] < 30) &
            (dataframe['volume'] > dataframe['volume_mean_slow'] * 2) &
            (dataframe['close'] > dataframe['open']) &  # Potvrda rasta
            (dataframe['close'] > dataframe['ema50'])   # Iznad EMA50
        )

        dataframe.loc[
            (hammer_signal | scalping_signal) & 
            (~self.market_crash) &
            (dataframe['volume'].rolling(3).mean() > dataframe['volume_mean_slow']),
            'enter_long'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Osnovni uslovi za izlaz
        exit_conditions = (
            (dataframe['close'] > dataframe['ema50']) |
            (dataframe['rsi'] > 60)
        )
        
        # Jak uptrend - ne izlazimo
        strong_uptrend = (
            (dataframe['close'] > dataframe['ema50']) &
            (dataframe['ema50'] > dataframe['ema200']) &
            (dataframe['rsi'] < 70)
        )
        
        # Višestruke padajuće sveće
        two_down_candles = (
            (dataframe['close'] < dataframe['open']) &
            (dataframe['close'].shift(1) < dataframe['open'].shift(1))
        )
        
        # Kombinacija uslova za izlaz
        dataframe.loc[
            (exit_conditions & ~strong_uptrend) | 
            (two_down_candles & (dataframe['rsi'] > 50)),
            'exit_long'
        ] = 1
        
        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                      current_rate: float, current_profit: float, **kwargs) -> float:
        # Dinamički trailing stop baziran na trendu
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        if (last_candle['close'] > last_candle['ema200'] and 
            last_candle['ema50'] > last_candle['ema200'] and
            last_candle['rsi'] < 70):
            return -0.03  # Širi stop u jakom uptrendu
        
        return -0.015  # Standardni stop

    @property
    def market_crash(self) -> bool:
        # Poboljšana detekcija pada tržišta
        btc_df = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe="5m")
        if btc_df is not None and len(btc_df) > 10:
            # Provjera za 3 od poslednjih 5 sveća padajuće
            last_candles = btc_df.iloc[-5:]
            down_candles = sum(last_candles['close'] < last_candles['open'])
            if down_candles >= 3:
                return True
            
            # Provjera za značajan pad u poslednjih 10 sveća
            last_close = btc_df['close'].iloc[-1]
            prev_close = btc_df['close'].iloc[-10]
            change = (last_close - prev_close) / prev_close
            if change < -0.03:
                return True
        return False
