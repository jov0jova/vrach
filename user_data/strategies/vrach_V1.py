'''
__________________________________________________________________________________________________________________
VRACH Trading Strategy.
__________________________________________________________________________________________________________________
Created by: jov0jova
Live version : 1.0.0
__________________________________________________________________________________________________________________
Trading strategy : "scalp", "position", "daytrade", "swing", "long"
__________________________________________________________________________________________________________________
'''
#Code

import numpy as np
import talib.abstract as ta
import pandas as pd
from freqtrade.strategy.interface import IStrategy
from freqtrade.strategy import merge_informative_pair
from pandas import DataFrame, Series
from functools import reduce
from freqtrade.persistence import Trade
from datetime import datetime, timedelta
from typing import Optional

class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    info_timeframes = ["15m","30m","1h","4h","8h","12h","1d","1w"]
    minimal_roi = {
        "480": 0.02,
        "240": 0.014,
        "60": 0.007,
        "0": 0.005
    }
    stoploss = -0.99
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

        # === RSI Indicators ===
        dataframe['rsi_14_5m'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['rsi_6_5m'] = ta.RSI(dataframe['close'], timeperiod=6)

        # === EMA Indicators ===
        dataframe['ema_20_5m'] = ta.EMA(dataframe['close'], timeperiod=20)
        dataframe['ema_50_5m'] = ta.EMA(dataframe['close'], timeperiod=50)
        dataframe['ema_200_5m'] = ta.EMA(dataframe['close'], timeperiod=200)

        # === MFI ===
        dataframe['mfi_5m'] = ta.MFI(dataframe['high'], dataframe['low'], dataframe['close'], dataframe['volume'], timeperiod=14)

        # === MACD ===
        macd = ta.MACD(dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd_5m'] = macd['macd']  # Ili macd['macd'] ako vraća DataFrame/Series sa tim imenima
        dataframe['macd_signal_5m'] = macd['macdsignal']# Ili macd['macdsignal']
        dataframe['macd_histogram_5m'] = macd['macd_histogram'] # Ili macd['macd_histogram']

        # === Bollinger Bands ===
        bb = ta.BBANDS(dataframe['close'], timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_5m'] = bb['BBU_20_2.0']  # Assuming upper band is the first element
        dataframe['bb_middle_5m'] = bb['BBM_20_2.0'] # Assuming middle band is the second element
        dataframe['bb_lower_5m'] = bb['BBL_20_2.0']  # Assuming lower band is the third element
        
        # === ATR ===
        dataframe['atr_14_5m'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)

        # === Informative columns to help with filtering ===
        dataframe['macd_cross_5m'] = np.where(dataframe['macd'] > dataframe['macd_signal'], 1, -1)
        dataframe['price_above_ema_200_5m'] = np.where(dataframe['close'] > dataframe['ema_200'], 1, 0)
        return dataframe

    def informative_indicators(self, metadata: dict, info_timeframe: str) -> DataFrame:

        pair = metadata['pair']
        ohlcv = self.dp.get_pair_dataframe(pair=pair, timeframe=info_timeframe)

        if ohlcv is None or len(ohlcv) == 0:
            return DataFrame()

        dataframe = ohlcv.copy()

        # === RSI Indicators ===
        dataframe['rsi_14'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['rsi_6'] = ta.RSI(dataframe['close'], timeperiod=6)

        # === EMA Indicators ===
        dataframe['ema_20'] = ta.EMA(dataframe['close'], timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe['close'], timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe['close'], timeperiod=200)

        # === MFI ===
        dataframe['mfi'] = ta.MFI(dataframe['high'], dataframe['low'], dataframe['close'], dataframe['volume'], timeperiod=14)

        # === MACD ===
        macd = ta.MACD(dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd['macd']  # Ili macd['macd'] ako vraća DataFrame/Series sa tim imenima
        dataframe['macd_signal'] = macd['macdsignal']# Ili macd['macdsignal']
        dataframe['macd_histogram'] = macd['macd_histogram'] # Ili macd['macd_histogram']

        # === Bollinger Bands ===
        bb = ta.BBANDS(dataframe['close'], timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper'] = bb['BBU_20_2.0']  # Assuming upper band is the first element
        dataframe['bb_middle'] = bb['BBM_20_2.0'] # Assuming middle band is the second element
        dataframe['bb_lower'] = bb['BBL_20_2.0']  # Assuming lower band is the third element
        
        # === ATR ===
        dataframe['atr_14'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)

        # === Informative columns to help with filtering ===
        dataframe['macd_cross'] = np.where(dataframe['macd'] > dataframe['macd_signal'], 1, -1)
        dataframe['price_above_ema_200'] = np.where(dataframe['close'] > dataframe['ema_200'], 1, 0)

        return dataframe

    def informative_15m_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "15m")

    def informative_30m_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "30m")

    def informative_1h_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "1h")

    def informative_4h_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "4h")

    def informative_8h_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "8h")

    def informative_12h_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "12h")

    def informative_1d_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "1d")

    def informative_1w_indicators(self, metadata: dict) -> DataFrame:
        return self.informative_indicators(metadata, "1w")

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        if dataframe.empty:
            return dataframe
        
        # ✅ SCALP TRADE — RSI oversold + BB touch + high volatility
        # Koristimo informative_5m (5 minuta) indikator
        scalp_cond = (
            (dataframe['rsi_14_5m'] < 30) &
            (dataframe['close'] < dataframe['bb_lower_5m']) &
            (dataframe['atr_14_5m'] > dataframe['atr_14_5m'].rolling(20).mean()) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[scalp_cond, 'enter_long'] = True
        dataframe.loc[scalp_cond, 'position_type'] = 'scalp'
        
        # ✅ POSITION TRADE — EMA50 < EMA200 + RSI recovery + MACD crossover
        # Koristimo informative_1h (1 sat) indikator
        informative_1h = self.informative_1h_indicators(metadata)
        
        dataframe = dataframe.merge(
            informative_1h[["ema_50", "ema_200", "rsi", "macd", "macd_signal"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1h")
        )
        
        position_cond = (
            (dataframe['ema_50_1h'] < dataframe['ema_200_1h']) &
            (dataframe['rsi_14_1h'] > 30) & (dataframe['rsi_1h'] < 50) &
            (dataframe['macd_1h'] > dataframe['macd_signal_1h']) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[position_cond, 'enter_long'] = True
        dataframe.loc[position_cond, 'position_type'] = 'position'

        # ✅ DAYTRADE — Trend reversal: RSI < 40 + BB lower bounce + MACD up + OBV rising
        # Koristimo informative_1h (1 sat) indikator
        
        informative_1h = self.informative_1h_indicators(metadata)
        
        dataframe = dataframe.merge(
            informative_1h[["bb_lower", "macd", "macd_signal", "obv_1h"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1h")
        )
        
        daytrade_cond = (
            (dataframe['rsi_14_1h'] < 40) &
            (dataframe['close'] <= dataframe['bb_lower_1h']) &
            (dataframe['macd_1h'] > dataframe['macd_signal_1h']) &
            (dataframe['obv_1h'] > dataframe['obv_1h'].shift(1)) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[daytrade_cond, 'enter_long'] = True
        dataframe.loc[daytrade_cond, 'position_type'] = 'daytrade'
        
        # ✅ SWING TRADE — EMA200 slope up + ADX > 25 + MACD > 0 + RSI 40–60
        # Koristimo informative_4h (4 sata) indikator
        
        informative_4h = self.informative_4h_indicators(metadata)
        
        dataframe = dataframe.merge(
            informative_4h[["ema_200", "adx_14", "macd", "rsi_14"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_4h")
        )
        
        swing_cond = (
            (dataframe['ema_200_4h'] > dataframe['ema_200_4h'].shift(1)) &
            (dataframe['adx_14_4h'] > 25) & (dataframe['macd_4h'] > 0) &
            (dataframe['rsi_14_4h'] > 40) & (dataframe['rsi_14_4h'] < 60) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[swing_cond, 'enter_long'] = True
        dataframe.loc[swing_cond, 'position_type'] = 'swing'
        
        # ✅ LONG TERM — EMA200 uptrend + RSI breakout + MACD > 0 + Price above BB middle
        # Koristimo informative_1d (1 dan) indikator
        
        informative_1d = self.informative_1d_indicators(metadata)
        dataframe = dataframe.merge(
            informative_1d[["ema_200", "rsi", "macd", "bb_middle"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1d")
        )
        long_cond = (
            (dataframe['ema_200_1d'] > dataframe['ema_200_1d'].shift(1)) &
            (dataframe['rsi__14_1d'] > 50) &
            (dataframe['macd_1d'] > dataframe['macd_signal_1d']) &
            (dataframe['close'] > dataframe['bb_middle_1d']) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[long_cond, 'enter_long'] = True
        dataframe.loc[long_cond, 'position_type'] = 'long'
        return dataframe


    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe
        # Dodavanje indikatora sa različitim vremenskim okvirima
        informative_1h = self.informative_1h_indicators(metadata)
        informative_4h = self.informative_4h_indicators(metadata)
        informative_1d = self.informative_1d_indicators(metadata)

        dataframe = dataframe.merge(
            informative_1h[["rsi_14_1h", "bb_upper_1h", "macd", "macd_signal", "obv_1h"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1h")
        )
        dataframe = dataframe.merge(
            informative_4h[["rsi_14_4h", "adx_14_4h", "macd", "macd_signal"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_4h")
        )
        dataframe = dataframe.merge(
            informative_1d[["rsi_14_1d", "ema_200_1d", "macd", "macd_signal", "obv_1d"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1d")
        )
        dataframe['exit_long'] = False
        # SCALP: Brzi profiti — izlazi kad RSI pređe 70 ili dođe do BB gornje
        scalp_exit = (
            (dataframe['position_type'] == 'scalp') &
            (
                (dataframe['rsi_14_5m'] > 70) |
                (dataframe['close'] > dataframe['bb_upper_5m']) |
                (dataframe['macd'] < dataframe['macd_signal'])  # gubi momentum
            )
        )
        dataframe.loc[scalp_exit, 'exit_long'] = True
        # POSITION: RSI previše visok, MACD se obrće, pad volumena
        position_exit = (
            (dataframe['position_type'] == 'position') &
            (
                (dataframe['rsi_14_1h'] > 65) &
                (dataframe['macd'] < dataframe['macd_signal']) |
                (dataframe['volume'] < dataframe['volume'].rolling(10).mean())
            )
        )
        dataframe.loc[position_exit, 'exit_long'] = True
        # DAYTRADE: RSI > 70 ili BB upper, pad OBV = gubitak snage
        daytrade_exit = (
            (dataframe['position_type'] == 'daytrade') &
            (
                (dataframe['rsi_14_1h'] > 70) |
                (dataframe['close'] > dataframe['bb_upper_1h']) |
                (dataframe['obv_1h'] < dataframe['obv_1h'].shift(1))
            )
        )
        dataframe.loc[daytrade_exit, 'exit_long'] = True
        # SWING: RSI > 75, ADX opada, MACD signal slabosti
        swing_exit = (
            (dataframe['position_type'] == 'swing') &
            (
                (dataframe['rsi_14_4h'] > 75) |
                (dataframe['adx_14_4h'] < dataframe['adx_14_4h'].shift(1)) |
                (dataframe['macd'] < dataframe['macd_signal'])
            )
        )
        dataframe.loc[swing_exit, 'exit_long'] = True
        # LONG: RSI > 80, pad trenda, price ispod EMA200, obv pada
        long_exit = (
            (dataframe['position_type'] == 'long') &
            (
                (dataframe['rsi_14_1d'] > 80) |
                (dataframe['close'] < dataframe['ema_200_1d']) |
                (dataframe['macd'] < dataframe['macd_signal']) |
                (dataframe['obv_1d'] < dataframe['obv_1d'].shift(1))
            )
        )
        dataframe.loc[long_exit, 'exit_long'] = True
        # DINAMIČKI SWITCH ako je strategija loša: Prebaci iz swing/long u position/daytrade ako indikatori slabe ali još nisu za sell
        # Ova logika je opcionalna, možemo je implementirati kasnije kroz `custom_exit()`
        return dataframe


    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty:
            return None

        # Dodavanje indikatora sa različitim vremenskim okvirima
        informative_1h = self.informative_1h_indicators(kwargs)
        informative_4h = self.informative_4h_indicators(kwargs)
        informative_1d = self.informative_1d_indicators(kwargs)
        
        dataframe = dataframe.merge(
            informative_1h[["rsi_14", "macd_histogram", "ema_50", "ema_200"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1h")
        )
        dataframe = dataframe.merge(
            informative_4h[["rsi_14", "macd_histogram", "ema_50", "ema_200"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_4h")
        )
        dataframe = dataframe.merge(
            informative_1d[["rsi_14", "macd_histogram", "ema_50", "ema_200"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1d")
        )
        last_candle = dataframe.iloc[-1]

        # ===== RISK MANAGEMENT =====

        # 1. Hitni izlaz ako je gubitak prevelik
        if current_profit < -0.08:
            return "emergency_loss_cut"
        
        # 2. RSI i trend pokazuju pad - izađi
        if last_candle['rsi_14_1h'] < 30 and last_candle['ema_50_1h'] < last_candle['ema_200_1h']:
            return "rsi_bear_exit"
        
        # 3. MACD histogram pada + RSI slabost
        if last_candle['macd_histogram_1h'] < 0 and last_candle['rsi_14_1h'] < 40:
            return "macd_rsi_exit"
        
        # 4. Pozicija traje predugo bez profita
        duration = (current_time - trade.open_date_utc).total_seconds() / 60  # u minutama
        if duration > 240 and current_profit < 0.005:
            return "timeout_exit"
        
        # 5. Predugo držimo poziciju bez napretka (Swing/Long)
        if trade.tag in ["swing", "long"] and duration > 1440 and current_profit < 0.01:
            return "long_timeout_exit"
        
        # ===== PROFIT TARGETS =====
        
        # 6. RSI Peak exit (zaključavanje profita)
        if current_profit > 0.04 and last_candle['rsi_14_1h'] > 75:
            return "take_profit_rsi_peak"
        
        # 7. RSI pada sa visokih vrednosti + CCI divergencija
        if last_candle['rsi_14_1h'] < 70 and last_candle['cci'] < 100 and current_profit > 0.03:
            return "momentum_loss_exit"
        
        # ===== POZICIJE SA ZADRŽAVANJEM =====
        
        # 8. Zadrži poziciju ako je u uzlaznom trendu
        if trade.tag in ["swing", "long"] and \
        last_candle['ema_50_1h'] > last_candle['ema_200_1h'] and \
        last_candle['rsi_14_1h'] > 55:
            return None  # ne izlazi
        
        # 9. Zadrži daytrade ako RSI i momentum još drže
        if trade.tag in ["daytrade", "position"] and \
        current_profit > 0.015 and last_candle['rsi_14_1h'] > 50:
            return None  # zadrži
        
        # 10. Scalp - brzi izlaz pri malom profitu
        if trade.tag == "scalp" and current_profit > 0.012:
            return "quick_scalp_exit"
        return None  # default: ne menjaj ništa
    
    def adjust_trade_position_type(self, trade: 'Trade', dataframe: DataFrame):
        
        last = dataframe.iloc[-1]
        current_type = trade.entry_tag
        
        # Dodavanje indikatora sa različitim vremenskim okvirima
        informative_1h = self.informative_1h_indicators(kwargs)
        informative_4h = self.informative_4h_indicators(kwargs)
        informative_1d = self.informative_1d_indicators(kwargs)
        

        dataframe = dataframe.merge(
            informative_1h[["rsi_14_1h", "macd_histogram", "ema_50", "ema_200"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1h")
        )
        dataframe = dataframe.merge(
            informative_4h[["rsi_14_4h", "macd_histogram", "ema_50", "ema_200"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_4h")
        )
        dataframe = dataframe.merge(
            informative_1d[["rsi_14_1d", "macd_histogram", "ema_50", "ema_200"]],
            left_index=True, right_index=True, how='left', suffixes=("", "_1d")
        )
        last = dataframe.iloc[-1]  # Update last to include new indicators
        
        # ===== SWING -> DAYTRADE =====
        if current_type == 'swing':
            if last['rsi_14_4h'] < 55 and last['macd_histogram_4h'] < 0:
                trade.entry_tag = 'daytrade'
                return "Switched swing -> daytrade"
        
        # ===== LONG -> SWING =====
        if current_type == 'long':
            if last['rsi_14_1d'] < 60 or last['ema_50_1d'] < last['ema_200_1d']:
                trade.entry_tag = 'swing'
                return "Switched long -> swing"
        
        # ===== SCALP -> POSITION =====
        if current_type == 'scalp':
            if last['rsi_14_5m'] < 50 and last['macd_histogram_5m'] < 0:
                trade.entry_tag = 'position'
                return "Switched scalp -> position"
        return None  # No change
