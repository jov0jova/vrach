from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'

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

    def __init__(self):
        self.peak_candles = []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)
        dataframe['volume_mean_slow'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['upper_wick'] = dataframe['high'] - dataframe[['close', 'open']].max(axis=1)
        dataframe['lower_wick'] = dataframe[['close', 'open']].min(axis=1) - dataframe['low']
        dataframe['body'] = abs(dataframe['close'] - dataframe['open'])

        self._identify_peak_candles(dataframe)
        
        return dataframe
	    
    def _identify_peak_candles(self, dataframe: DataFrame):
        # Consider candles with the highest close in the last 10 candles as "peak" candles
        window_size = 10
        peak_window = dataframe['close'].rolling(window=window_size).max()
        peak_candles = dataframe[dataframe['close'] == peak_window]

        for _, row in peak_candles.iterrows():
            # Store the RSI and EMA values when a peak candle is identified
            self.peak_candles.append({
                'timestamp': row.name,
                'rsi': row['rsi'],
                'ema50': row['ema50'],
                'ema200': row['ema200']
            })
		
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
        for peak in self.peak_candles:
            # Calculate 90% of peak RSI and EMA values
            rsi_threshold = peak['rsi'] * 0.90
            ema50_threshold = peak['ema50'] * 0.90
            ema200_threshold = peak['ema200'] * 0.90

            # Exit if current RSI is above 90% of the peak RSI and price is near the 90% threshold
            dataframe.loc[
                (dataframe['close'] > ema50_threshold) & 
                (dataframe['rsi'] > rsi_threshold) & 
                (dataframe['ema50'] > ema50_threshold),
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
            if change < -0.02:
                return True
        return False
		
		
		
		
