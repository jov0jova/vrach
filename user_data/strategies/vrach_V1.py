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

from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.optimize.space import Categorical, Real
import numpy as np
from datetime import datetime, timedelta
from freqtrade.persistence import Trade


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
        dataframe['rsi_14'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['rsi_6'] = ta.RSI(dataframe['close'], timeperiod=6)

        # === EMA Indicators ===
        dataframe['ema_20'] = ta.EMA(dataframe['close'], timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe['close'], timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe['close'], timeperiod=200)

        # === MFI ===
        dataframe['mfi'] = ta.MFI(dataframe['high'], dataframe['low'], dataframe['close'], dataframe['volume'], timeperiod=14)

        # === MACD ===
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']  # Ili macd['macd'] ako vraća DataFrame/Series sa tim imenima
        dataframe['macd_signal'] = macd['macdsignal']# Ili macd['macdsignal']
        dataframe['macd_histogram'] = macd['macdhist'] # Ili macd['macd_histogram']

        # === Bollinger Bands ===
        dataframe['bb_upper'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['upperband']
        dataframe['bb_middle'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['middleband']
        dataframe['bb_lower'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['lowerband']
        
        # === ATR ===
        dataframe['atr_14'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)

        # === ADX ===
        dataframe['adx_14'] = ta.ADX(dataframe,timeperiod=14)

        # === OBV ===
        dataframe['obv'] = ta.OBV(dataframe)
        # === Informative columns to help with filtering ===
        #dataframe['macd_cross_5m'] = np.where(dataframe['macd'] > dataframe['macd_signal'], 1, -1)
        #dataframe['price_above_ema_200_5m'] = np.where(dataframe['close'] > dataframe['ema_200'], 1, 0)
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
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']  # Ili macd['macd'] ako vraća DataFrame/Series sa tim imenima
        dataframe['macd_signal'] = macd['macdsignal']# Ili macd['macdsignal']
        dataframe['macd_histogram'] = macd['macdhist'] # Ili macd['macd_histogram']

        # === Bollinger Bands ===
        dataframe['bb_upper'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['upperband']
        dataframe['bb_middle'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['middleband']
        dataframe['bb_lower'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['lowerband']
        
        # === ATR ===
        dataframe['atr_14'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)

        # === ADX ===
        dataframe['adx_14'] = ta.ADX(dataframe,timeperiod=14)

        # === OBV ===
        dataframe['obv'] = ta.OBV(dataframe)

        # === Informative columns to help with filtering ===
        #dataframe['macd_cross'] = np.where(dataframe['macd'] > dataframe['macd_signal'], 1, -1)
        #dataframe['price_above_ema_200'] = np.where(dataframe['close'] > dataframe['ema_200'], 1, 0)

        return dataframe

    def informative_15m_indicators(self, metadata: dict) -> DataFrame:
        dataframe_15m = self.informative_indicators(metadata, "15m")
        dataframe_15m = dataframe_15m.rename(columns={
            "ema_50": "ema_50_15m",
            "ema_200": "ema_200_15m",
            "rsi_14": "rsi_14_15m",
            "macd": "macd_15m",
            "macd_signal": "macd_signal_15m",
            "bb_lower": "bb_lower_15m",
            "obv": "obv_15m",
            "bb_upper": "bb_upper_15m",
            "adx_14": "adx_14_15m",
            "atr_14": "atr_14_15m",
            "rsi_6": "rsi_6_15m",
            "ema_20": "ema_20_15m",
            "mfi": "mfi_15m",
            "macd_histogram": "macd_histogram_15m",
            "bb_middle": "bb_middle_15m"
        })
        return dataframe_15m

    def informative_30m_indicators(self, metadata: dict) -> DataFrame:
        dataframe_30m = self.informative_indicators(metadata, "30m")
        dataframe_30m = dataframe_30m.rename(columns={
            "ema_50": "ema_50_30m",
            "ema_200": "ema_200_30m",
            "rsi_14": "rsi_14_30m",
            "macd": "macd_30m",
            "macd_signal": "macd_signal_30m",
            "bb_lower": "bb_lower_30m",
            "obv": "obv_30m",
            "bb_upper": "bb_upper_30m",
            "adx_14": "adx_14_30m",
            "atr_14": "atr_14_30m",
            "rsi_6": "rsi_6_30m",
            "ema_20": "ema_20_30m",
            "mfi": "mfi_30m",
            "macd_histogram": "macd_histogram_30m",
            "bb_middle": "bb_middle_30m"
        })
        return dataframe_30m

    def informative_1h_indicators(self, metadata: dict) -> DataFrame:
        dataframe_1h = self.informative_indicators(metadata, "1h")
        dataframe_1h = dataframe_1h.rename(columns={
            "ema_50": "ema_50_1h",
            "ema_200": "ema_200_1h",
            "rsi_14": "rsi_14_1h",
            "macd": "macd_1h",
            "macd_signal": "macd_signal_1h",
            "bb_lower": "bb_lower_1h",
            "obv": "obv_1h",
            "bb_upper": "bb_upper_1h",
            "adx_14": "adx_14_1h",
            "atr_14": "atr_14_1h",
            "rsi_6": "rsi_6_1h",
            "ema_20": "ema_20_1h",
            "mfi": "mfi_1h",
            "macd_histogram": "macd_histogram_1h",
            "bb_middle": "bb_middle_1h"
        })
        return dataframe_1h

    def informative_4h_indicators(self, metadata: dict) -> DataFrame:
        dataframe_4h = self.informative_indicators(metadata, "4h")
        dataframe_4h = dataframe_4h.rename(columns={
            "ema_50": "ema_50_4h",
            "ema_200": "ema_200_4h",
            "rsi_14": "rsi_14_4h",
            "macd": "macd_4h",
            "macd_signal": "macd_signal_4h",
            "bb_lower": "bb_lower_4h",
            "obv": "obv_4h",
            "bb_upper": "bb_upper_4h",
            "adx_14": "adx_14_4h",
            "atr_14": "atr_14_4h",
            "rsi_6": "rsi_6_4h",
            "ema_20": "ema_20_4h",
            "mfi": "mfi_4h",
            "macd_histogram": "macd_histogram_4h",
            "bb_middle": "bb_middle_4h"
        })
        return dataframe_4h

    def informative_8h_indicators(self, metadata: dict) -> DataFrame:
        dataframe_8h = self.informative_indicators(metadata, "8h")
        dataframe_8h = dataframe_8h.rename(columns={
            "ema_50": "ema_50_8h",
            "ema_200": "ema_200_8h",
            "rsi_14": "rsi_14_8h",
            "macd": "macd_8h",
            "macd_signal": "macd_signal_8h",
            "bb_lower": "bb_lower_8h",
            "obv": "obv_8h",
            "bb_upper": "bb_upper_8h",
            "adx_14": "adx_14_8h",
            "atr_14": "atr_14_8h",
            "rsi_6": "rsi_6_8h",
            "ema_20": "ema_20_8h",
            "mfi": "mfi_8h",
            "macd_histogram": "macd_histogram_8h",
            "bb_middle": "bb_middle_8h"
        })
        return dataframe_8h

    def informative_12h_indicators(self, metadata: dict) -> DataFrame:
        dataframe_12h = self.informative_indicators(metadata, "12h")
        dataframe_12h = dataframe_12h.rename(columns={
            "ema_50": "ema_50_12h",
            "ema_200": "ema_200_12h",
            "rsi_14": "rsi_14_12h",
            "macd": "macd_12h",
            "macd_signal": "macd_signal_12h",
            "bb_lower": "bb_lower_12h",
            "obv": "obv_12h",
            "bb_upper": "bb_upper_12h",
            "adx_14": "adx_14_12h",
            "atr_14": "atr_14_12h",
            "rsi_6": "rsi_6_12h",
            "ema_20": "ema_20_12h",
            "mfi": "mfi_12h",
            "macd_histogram": "macd_histogram_12h",
            "bb_middle": "bb_middle_12h"
        })
        return dataframe_12h

    def informative_1d_indicators(self, metadata: dict) -> DataFrame:
        dataframe_1d = self.informative_indicators(metadata, "1d")
        dataframe_1d = dataframe_1d.rename(columns={
            "ema_50": "ema_50_1d",
            "ema_200": "ema_200_1d",
            "rsi_14": "rsi_14_1d",
            "macd": "macd_1d",
            "macd_signal": "macd_signal_1d",
            "bb_lower": "bb_lower_1d",
            "obv": "obv_1d",
            "bb_upper": "bb_upper_1d",
            "adx_14": "adx_14_1d",
            "atr_14": "atr_14_1d",
            "rsi_6": "rsi_6_1d",
            "ema_20": "ema_20_1d",
            "mfi": "mfi_1d",
            "macd_histogram": "macd_histogram_1d",
            "bb_middle": "bb_middle_1d"
        })
        return dataframe_1d

    def informative_1w_indicators(self, metadata: dict) -> DataFrame:
        dataframe_1w = self.informative_indicators(metadata, "1w")
        dataframe_1w = dataframe_1w.rename(columns={
            "ema_50": "ema_50_1w",
            "ema_200": "ema_200_1w",
            "rsi_14": "rsi_14_1w",
            "macd": "macd_1w",
            "macd_signal": "macd_signal_1w",
            "bb_lower": "bb_lower_1w",
            "obv": "obv_1w",
            "bb_upper": "bb_upper_1w",
            "adx_14": "adx_14_1w",
            "atr_14": "atr_14_1w",
            "rsi_6": "rsi_6_1w",
            "ema_20": "ema_20_1w",
            "mfi": "mfi_1w",
            "macd_histogram": "macd_histogram_1w",
            "bb_middle": "bb_middle_1w"
        })
        return dataframe_1w

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe

        informative_1h = self.informative_1h_indicators(metadata)
        informative_4h = self.informative_4h_indicators(metadata)
        informative_1d = self.informative_1d_indicators(metadata)

        # ✅ SCALP TRADE
        scalp_cond = (
            (dataframe['rsi_14'] < 30) &
            (dataframe['close'] < dataframe['bb_lower']) &
            (dataframe['atr_14'] > dataframe['atr_14'].rolling(20).mean()) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[scalp_cond, 'enter_long'] = True
        dataframe.loc[scalp_cond, 'position_type'] = 'scalp'

        # ✅ POSITION TRADE
        position_cond = (
            (informative_1h['ema_50_1h'].iloc[-1] < informative_1h['ema_200_1h'].iloc[-1]) &
            (informative_1h['rsi_14_1h'].iloc[-1] > 30) & (informative_1h['rsi_14_1h'].iloc[-1] < 50) &
            (informative_1h['macd_1h'].iloc[-1] > informative_1h['macd_signal_1h'].iloc[-1]) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[position_cond, 'enter_long'] = True
        dataframe.loc[position_cond, 'position_type'] = 'position'

        # ✅ DAYTRADE
        daytrade_cond = (
            (informative_1h['rsi_14_1h'].iloc[-1] < 40) &
            (dataframe['close'] <= informative_1h['bb_lower_1h'].iloc[-1]) &
            (informative_1h['macd_1h'].iloc[-1] > informative_1h['macd_signal_1h'].iloc[-1]) &
            (informative_1h['obv_1h'].iloc[-1] > informative_1h['obv_1h'].shift(1).iloc[-1]) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[daytrade_cond, 'enter_long'] = True
        dataframe.loc[daytrade_cond, 'position_type'] = 'daytrade'

        # ✅ SWING TRADE
        swing_cond = (
            (informative_4h['ema_200_4h'].iloc[-1] > informative_4h['ema_200_4h'].shift(1).iloc[-1]) &
            (informative_4h['adx_14_4h'].iloc[-1] > 25) &
            (informative_4h['macd_4h'].iloc[-1] > 0) &
            (informative_4h['rsi_14_4h'].iloc[-1] > 40) & (informative_4h['rsi_14_4h'].iloc[-1] < 60) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[swing_cond, 'enter_long'] = True
        dataframe.loc[swing_cond, 'position_type'] = 'swing'

        # ✅ LONG TERM
        long_cond = (
            (informative_1d['ema_200_1d'].iloc[-1] > informative_1d['ema_200_1d'].shift(1).iloc[-1]) &
            (informative_1d['rsi_14_1d'].iloc[-1] > 50) &
            (informative_1d['macd_1d'].iloc[-1] > informative_1d['macd_signal_1d'].iloc[-1]) &
            (dataframe['close'] > informative_1d['bb_middle_1d'].iloc[-1]) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[long_cond, 'enter_long'] = True
        dataframe.loc[long_cond, 'position_type'] = 'long'

        return dataframe


    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe

        informative_1h = self.informative_1h_indicators(metadata)
        informative_4h = self.informative_4h_indicators(metadata)
        informative_1d = self.informative_1d_indicators(metadata)

        dataframe['exit_long'] = False

        # SCALP: Brzi profiti — izlazi kad RSI pređe 70 ili dođe do BB gornje
        scalp_exit = (
            (dataframe['position_type'] == 'scalp') &
            (
                (dataframe['rsi_14'] > 70) |
                (dataframe['close'] > dataframe['bb_upper']) |
                (dataframe['macd'] < dataframe['macd_signal'])  # gubi momentum
            )
        )
        dataframe.loc[scalp_exit, 'exit_long'] = True

        # POSITION: RSI previše visok, MACD se obrće, pad volumena
        position_exit = (
            (dataframe['position_type'] == 'position') &
            (
                (informative_1h['rsi_14_1h'] > 65) &
                (dataframe['macd'] < dataframe['macd_signal']) |
                (dataframe['volume'] < dataframe['volume'].rolling(10).mean())
            )
        )
        dataframe.loc[position_exit, 'exit_long'] = True

        # DAYTRADE: RSI > 70 ili BB upper, pad OBV = gubitak snage
        daytrade_exit = (
            (dataframe['position_type'] == 'daytrade') &
            (
                (informative_1h['rsi_14_1h'] > 70) |
                (dataframe['close'] > informative_1h['bb_upper_1h']) |
                (informative_1h['obv_1h'] < informative_1h['obv_1h'].shift(1))
            )
        )
        dataframe.loc[daytrade_exit, 'exit_long'] = True

        # SWING: RSI > 75, ADX opada, MACD signal slabosti
        swing_exit = (
            (dataframe['position_type'] == 'swing') &
            (
                (informative_4h['rsi_14_4h'] > 75) |
                (informative_4h['adx_14_4h'] < informative_4h['adx_14_4h'].shift(1)) |
                (dataframe['macd'] < dataframe['macd_signal'])
            )
        )
        dataframe.loc[swing_exit, 'exit_long'] = True

        # LONG: RSI > 80, pad trenda, price ispod EMA200, obv pada
        long_exit = (
            (dataframe['position_type'] == 'long') &
            (
                (informative_1d['rsi_14_1d'] > 80) |
                (dataframe['close'] < informative_1d['ema_200_1d']) |
                (dataframe['macd'] < dataframe['macd_signal']) |
                (informative_1d['obv_1d'] < informative_1d['obv_1d'].shift(1))
            )
        )
        dataframe.loc[long_exit, 'exit_long'] = True

        # DINAMIČKI SWITCH ako je strategija loša: Prebaci iz swing/long u position/daytrade ako indikatori slabe ali još nisu za sell
        # Ova logika je opcionalna, možemo je implementirati kasnije kroz `custom_exit()`
        return dataframe


    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime, current_rate: float,
                    current_profit: float, metadata: dict, **kwargs):

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty:
            return None

        informative_1h = self.informative_1h_indicators(metadata)
        informative_4h = self.informative_4h_indicators(metadata)
        informative_1d = self.informative_1d_indicators(metadata)

        last_candle = dataframe.iloc[-1]

        # ===== RISK MANAGEMENT =====

        # 1. Hitni izlaz ako je gubitak prevelik
        if current_profit < -0.08:
            return "emergency_loss_cut"

        # 2. RSI i trend pokazuju pad - izađi
        if last_candle['rsi_14_1h'] < 30 and informative_1h['ema_50_1h'].iloc[-1] < informative_1h['ema_200_1h'].iloc[-1]:
            return "rsi_bear_exit"

        # 3. MACD histogram pada + RSI slabost
        if informative_1h['macd_histogram_1h'].iloc[-1] < 0 and informative_1h['rsi_14_1h'].iloc[-1] < 40:
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
        if current_profit > 0.04 and informative_1h['rsi_14_1h'].iloc[-1] > 75:
            return "take_profit_rsi_peak"

        # 7. RSI pada sa visokih vrednosti + CCI divergencija
        # Pretpostavljam da imate 'cci' u vašem osnovnom dataframe-u
        if last_candle['rsi_14_1h'] < 70 and last_candle['cci'] < 100 and current_profit > 0.03:
            return "momentum_loss_exit"

        # ===== POZICIJE SA ZADRŽAVANJEM =====

        # 8. Zadrži poziciju ako je u uzlaznom trendu
        if trade.tag in ["swing", "long"] and \
        informative_1h['ema_50_1h'].iloc[-1] > informative_1h['ema_200_1h'].iloc[-1] and \
        informative_1h['rsi_14_1h'].iloc[-1] > 55:
            return None  # ne izlazi

        # 9. Zadrži daytrade ako RSI i momentum još drže
        if trade.tag in ["daytrade", "position"] and \
        current_profit > 0.015 and informative_1h['rsi_14_1h'].iloc[-1] > 50:
            return None  # zadrži

        # 10. Scalp - brzi izlaz pri malom profitu
        if trade.tag == "scalp" and current_profit > 0.012:
            return "quick_scalp_exit"
        return None  # default: ne menjaj ništa
    
    def adjust_trade_position_type(self, trade: 'Trade', dataframe: DataFrame, metadata: dict, **kwargs):

        last = dataframe.iloc[-1]
        current_type = trade.entry_tag

        informative_1h = self.informative_1h_indicators(metadata)
        informative_4h = self.informative_4h_indicators(metadata)
        informative_1d = self.informative_1d_indicators(metadata)

        # ===== SWING -> DAYTRADE =====
        if current_type == 'swing':
            if informative_4h['rsi_14_4h'].iloc[-1] < 55 and informative_4h['macd_histogram_4h'].iloc[-1] < 0:
                trade.entry_tag = 'daytrade'
                return "Switched swing -> daytrade"

        # ===== LONG -> SWING =====
        if current_type == 'long':
            if informative_1d['rsi_14_1d'].iloc[-1] < 60 or informative_1d['ema_50_1d'].iloc[-1] < informative_1d['ema_200_1d'].iloc[-1]:
                trade.entry_tag = 'swing'
                return "Switched long -> swing"

        # ===== SCALP -> POSITION =====
        if current_type == 'scalp':
            if last['rsi_14'] < 50 and dataframe['macd_histogram'].iloc[-1] < 0:
                trade.entry_tag = 'position'
                return "Switched scalp -> position"
        return None  # No change
