from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'

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
            'stoploss': Real(-0.05, -0.01),
            'trailing_stop': Categorical([True, False]),
            'trailing_stop_positive': Real(0.01, 0.08),
            'trailing_stop_positive_offset': Real(0.015, 0.1),
            # Hyperopt parametri za EMA periode
            'ema50_period': Categorical([30, 50, 75, 100]),
            'ema200_period': Categorical([150, 200, 250, 300]),
            # Hyperopt parametri za RSI pragove za ulazak
            'rsi_entry': Categorical([30, 35, 40]),
            'rsi_fast_entry': Categorical([25, 30, 35]),
            # Hyperopt parametri za RSI pragove za izlazak
            'rsi_exit': Categorical([60, 65, 70]),
            'rsi_peak_exit_high': Categorical([70, 75, 80, 85]),
            'rsi_peak_exit_low': Categorical([75, 80, 85, 90]),
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

        # Dodajemo RSI za prethodni period za detekciju divergencije
        dataframe['rsi_prev'] = dataframe['rsi'].shift(1)
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
        # Uslovi za izlazak bazirani na potencijalnom vrhuncu
        peak_exit_condition = (
            (dataframe['close'] < dataframe['close'].shift(1)) &  # Cena pala u odnosu na prethodnu svecu
            (dataframe['rsi'] > 70)  # RSI je u prekupljenoj zoni
        ) | (
            (dataframe['rsi'] > 80) & (dataframe['rsi'] < dataframe['rsi_prev']) # RSI opada iz ekstremne prekupljenosti
        )

        # Dodajemo i originalne uslove za izlazak, ali sa manjim prioritetom
        original_exit_condition = (dataframe['close'] > dataframe['ema50']) | (dataframe['rsi'] > 60)

        dataframe.loc[
            peak_exit_condition | (original_exit_condition & (dataframe['rsi'] > 65)), # Blago pooštravanje originalnog RSI uslova
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
