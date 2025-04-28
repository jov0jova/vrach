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

    peak_candles = []  # List to store peak candle parameters

    def hyperopt_parameters(self):
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
        return [("BTC/USDT", "5m"), ("BTC/USDT", "240m")]  # Added 4H timeframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)
        dataframe['volume_mean_slow'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['upper_wick'] = dataframe['high'] - dataframe[['close', 'open']].max(axis=1)
        dataframe['lower_wick'] = dataframe[['close', 'open']].min(axis=1) - dataframe['low']
        dataframe['body'] = abs(dataframe['close'] - dataframe['open'])

        # Identify peak candles in 4-hour timeframe
        self._identify_peak_candles(dataframe)
        
        return dataframe

    def _identify_peak_candles(self, dataframe: DataFrame):
        # Fetch the 4-hour timeframe data for more significant trend analysis
        btc_4h_df = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe="240m")

        if btc_4h_df is not None:
            # Consider candles with the highest close in the last 5 peaks (4-hour candles)
            peak_window = btc_4h_df['close'].rolling(window=5).max()
            peak_candles = btc_4h_df[btc_4h_df['close'] == peak_window]

            # Store peak candles' RSI, EMA50, and EMA200 values
            for _, row in peak_candles.iterrows():
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
            (hammer_signal | scalping_signal),
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
