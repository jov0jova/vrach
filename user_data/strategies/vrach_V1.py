from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real
from freqtrade.persistence import Trade
from datetime import datetime

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'

    minimal_roi = {
        "480": 0.02,
        "240": 0.014,
        "60": 0.007,
        "0": 0.005
    }

    stoploss = -0.10

    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    use_custom_stoploss = False
    can_short = False
    process_only_new_candles = True

    @staticmethod
    def hyperopt_parameters():
        return {
            'minimal_roi': {
                '0': Real(0.02, 0.1),
                '10': Real(0.01, 0.05),
                '20': Real(0, 0.03),
            },
            'stoploss': Real(-0.10, -0.05),
            'trailing_stop': Categorical([True, False]),
            'trailing_stop_positive': Real(0.01, 0.08),
            'trailing_stop_positive_offset': Real(0.015, 0.1),
            'ema50_period': Categorical([30, 50, 75, 100]),
            'ema200_period': Categorical([150, 200, 250, 300]),
            'rsi_entry': Categorical([30, 35, 40]),
            'rsi_fast_entry': Categorical([25, 30, 35]),
            'rsi_exit': Categorical([60, 65, 70]),
            'rsi_peak_exit_high': Categorical([70, 75, 80, 85]),
            'rsi_peak_exit_low': Categorical([75, 80, 85, 90]),
        }

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe, timeperiod=5)
        dataframe['volume_mean_slow'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['upper_wick'] = dataframe['high'] - dataframe[['close', 'open']].max(axis=1)
        dataframe['lower_wick'] = dataframe[['close', 'open']].min(axis=1) - dataframe['low']
        dataframe['body'] = abs(dataframe['close'] - dataframe['open'])
        dataframe['rsi_prev'] = dataframe['rsi'].shift(1)

        dataframe['daily_range'] = dataframe['high'] - dataframe['low']
        dataframe['adr'] = dataframe['daily_range'].rolling(window=288).mean()

        # Dinamički threshold za ADR
        dataframe['adr_volatility'] = dataframe['daily_range'].rolling(window=288).std()
        dataframe['adr_mean'] = dataframe['daily_range'].rolling(window=288).mean()
        dataframe['dynamic_adr_threshold'] = 0.85 + (dataframe['adr_volatility'] / dataframe['adr_mean']) * 0.5

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        hammer_signal = (
            (dataframe['close'] < dataframe['ema200']) &
            (dataframe['rsi'] < 30) &
            (dataframe['volume'] > dataframe['volume_mean_slow'] * 1.5) &
            (dataframe['lower_wick'] > dataframe['body'] * 1.5)
        )

        scalping_signal = (
            (dataframe['rsi_fast'] < 28) &
            (dataframe['volume'] > dataframe['volume_mean_slow'] * 2)
        )

        adr_filter = (
            (dataframe['adr'].notnull()) &
            (dataframe['daily_range'] > dataframe['adr'] * dataframe['dynamic_adr_threshold'])
        )

        dataframe.loc[
            (hammer_signal | scalping_signal) & adr_filter,
            'enter_long'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        peak_exit_condition = (
            (dataframe['close'] < dataframe['close'].shift(1)) & 
            (dataframe['rsi'] > 68)
        ) | (
            (dataframe['rsi'] > 66) & (dataframe['rsi'] < dataframe['rsi_prev'])
        )

        original_exit_condition = (
            (dataframe['close'] > dataframe['ema50']) | (dataframe['rsi'] > 60)
        )

        dataframe.loc[
            peak_exit_condition | (original_exit_condition & (dataframe['rsi'] > 78)),
            'exit_long'
        ] = 1

        return dataframe
