# --- Imporţi
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import pandas as pd
import numpy as np
import talib.abstract as ta

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3

    # Optimizacija
    peak_pullback_lookback = IntParameter(5, 50, default=20, space="buy")
    pullback_amount = DecimalParameter(0.001, 0.05, default=0.02, decimals=3, space="sell")

    # Config Settings
    timeframe = '5m'
    minimal_roi = {
        "0": 0.012  # Samo 1% minimum (manje očekivanje kad nema mnogo exit indikatora)
    }
    stoploss = -0.99  # Hard stoploss
    trailing_stop = False  # Mi koristimo custom trailing

    process_only_new_candles = True
    use_custom_exit = True

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=26)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                (dataframe['ema_fast'] > dataframe['ema_slow']) &
                (dataframe['rsi'] < 70) &
                (dataframe['close'] > dataframe['ema_fast'])
            ),
            'enter_long'
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['exit_long'] = 0  # Ne koristimo standardni exit
        return dataframe

    def custom_exit(self, pair: str, trade, current_time: 'datetime', current_rate: float,
                    current_profit: float, **kwargs):
        """
        Custom exit koji hvata najviši peak, čeka pullback, i tada izlazi.
        """

        # Učitaj prošle profita
        trade_custom = trade.custom_exit_info or {}

        # Ako nemamo podatke, inicijalizuj
        if not trade_custom:
            trade_custom['peak_profit'] = current_profit
            return None  # Ne izlazimo odmah

        # Ako imamo, updejtuj maksimalni peak
        if current_profit > trade_custom['peak_profit']:
            trade_custom['peak_profit'] = current_profit

        # Ako je profit pao za pullback_amount od peaka - izlazimo
        pullback_trigger = self.pullback_amount.value
        if current_profit <= (trade_custom['peak_profit'] - pullback_trigger):
            return "peak-pullback-exit"

        # Ako nismo još pala dovoljno, ostani unutra
        trade.update_custom_exit_info(trade_custom)
        return None
