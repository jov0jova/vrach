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
from freqtrade.strategy import merge_informative_pair


class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    inf_timeframes = ['15m','30m','1h', '4h','8h','12h', '1d','1w']
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
        pairs = [(pair, tf) for pair in self.dp.current_whitelist() for tf in self.inf_timeframes]
        return pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Glavni timeframe indikatori (5m)
        dataframe['ema_10'] = ta.EMA(dataframe, timeperiod=10)
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['rsi_14'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_6'] = ta.RSI(dataframe, timeperiod=6)
        dataframe['mfi'] = ta.MFI(dataframe)
        dataframe['adx_14'] = ta.ADX(dataframe)
        dataframe['atr_14'] = ta.ATR(dataframe)

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_histogram'] = macd['macdhist']

        bb = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_lower'] = bb['lowerband']

        # OBV (posebno jer nije deo ta lib)
        dataframe['obv'] = dataframe['volume'].combine_first(dataframe['volume'].shift()).fillna(0).cumsum()

        # Informativni timeframe-ovi
        for tf in self.inf_timeframes:
            informative = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=tf)

            informative[f'ema_20_{tf}'] = ta.EMA(informative, timeperiod=20)
            informative[f'ema_50_{tf}'] = ta.EMA(informative, timeperiod=50)
            informative[f'ema_200_{tf}'] = ta.EMA(informative, timeperiod=200)
            informative[f'rsi_14_{tf}'] = ta.RSI(informative, timeperiod=14)
            informative[f'rsi_6_{tf}'] = ta.RSI(informative, timeperiod=6)
            informative[f'mfi_{tf}'] = ta.MFI(informative)
            informative[f'adx_14_{tf}'] = ta.ADX(informative)
            informative[f'atr_14_{tf}'] = ta.ATR(informative)

            macd_inf = ta.MACD(informative)
            informative[f'macd_{tf}'] = macd_inf['macd']
            informative[f'macd_signal_{tf}'] = macd_inf['macdsignal']
            informative[f'macd_histogram_{tf}'] = macd_inf['macdhist']

            bb_inf = ta.BBANDS(informative, timeperiod=20)
            informative[f'bb_upper_{tf}'] = bb_inf['upperband']
            informative[f'bb_middle_{tf}'] = bb_inf['middleband']
            informative[f'bb_lower_{tf}'] = bb_inf['lowerband']

            informative[f'obv_{tf}'] = informative['volume'].combine_first(informative['volume'].shift()).fillna(0).cumsum()

            dataframe = merge_informative_pair(dataframe, informative, self.timeframe, tf, ffill=True)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe

        dataframe['enter_long'] = False
        dataframe['enter_tag'] = ''
        dataframe['position_type'] = ''

        # ✅ SCALP TRADE
        scalp_cond = (
            (dataframe['rsi_14'] < 30) &
            (dataframe['close'] < dataframe['bb_lower']) &
            (dataframe['atr_14'] > dataframe['atr_14'].rolling(20).mean()) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[scalp_cond, ['enter_long', 'enter_tag', 'position_type']] = (True, 'scalp', 'scalp')

        # ✅ POSITION TRADE
        position_cond = (
            (dataframe['ema_50_1h'] < dataframe['ema_200_1h']) &
            (dataframe['rsi_14_1h'] > 30) & (dataframe['rsi_14_1h'] < 50) &
            (dataframe['macd_1h'] > dataframe['macd_signal_1h']) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[position_cond, ['enter_long', 'enter_tag', 'position_type']] = (True, 'position', 'position')

        # ✅ DAYTRADE
        daytrade_cond = (
            (dataframe['rsi_14_1h'] < 40) &
            (dataframe['close'] <= dataframe['bb_lower_1h']) &
            (dataframe['macd_1h'] > dataframe['macd_signal_1h']) &
            (dataframe['obv_1h'] > dataframe['obv_1h'].shift(1)) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[daytrade_cond, ['enter_long', 'enter_tag', 'position_type']] = (True, 'daytrade', 'daytrade')

        # ✅ SWING TRADE
        swing_cond = (
            (dataframe['ema_200_4h'] > dataframe['ema_200_4h'].shift(1)) &
            (dataframe['adx_14_4h'] > 25) &
            (dataframe['macd_4h'] > 0) &
            (dataframe['rsi_14_4h'] > 40) & (dataframe['rsi_14_4h'] < 60) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[swing_cond, ['enter_long', 'enter_tag', 'position_type']] = (True, 'swing', 'swing')

        # ✅ LONG TERM
        long_cond = (
            (dataframe['ema_200_1d'] > dataframe['ema_200_1d'].shift(1)) &
            (dataframe['rsi_14_1d'] > 50) &
            (dataframe['macd_1d'] > dataframe['macd_signal_1d']) &
            (dataframe['close'] > dataframe['bb_middle_1d']) &
            (dataframe['volume'] > 0)
        )
        dataframe.loc[long_cond, ['enter_long', 'enter_tag', 'position_type']] = (True, 'long', 'long')

        return dataframe
'''
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe

        informative_1h = self.informative_1h_indicators(metadata)
        informative_4h = self.informative_4h_indicators(metadata)
        informative_1d = self.informative_1d_indicators(metadata)

        dataframe['exit_long'] = False
        dataframe['exit_tag'] = None  # Inicijalizujte kolonu exit_tag

        # SCALP: Brzi profiti — izlazi kad RSI pređe 70 ili dođe do BB gornje
        scalp_exit = (
            (dataframe['position_type'] == 'scalp') &
            (
                (dataframe['rsi_14'] > 70) |
                (dataframe['close'] > dataframe['bb_upper']) |
                (dataframe['macd'] < dataframe['macd_signal'])  # gubi momentum
            )
        )
        dataframe.loc[scalp_exit, ['exit_long', 'exit_tag']] = (True, 'scalp_exit')

        # POSITION: RSI previše visok, MACD se obrće, pad volumena
        position_exit = (
            (dataframe['position_type'] == 'position') &
            (
                (not informative_1h.empty and 'rsi_14_1h' in informative_1h.columns and not informative_1h['rsi_14_1h'].empty and informative_1h['rsi_14_1h'].iloc[-1] > 65) &
                (dataframe['macd'] < dataframe['macd_signal']) |
                (dataframe['volume'] < dataframe['volume'].rolling(10).mean())
            )
        )
        dataframe.loc[position_exit, ['exit_long', 'exit_tag']] = (True, 'position_exit')

        # DAYTRADE: RSI > 70 ili BB upper, pad OBV = gubitak snage
        daytrade_exit = (
            (dataframe['position_type'] == 'daytrade') &
            (
                (not informative_1h.empty and 'rsi_14_1h' in informative_1h.columns and not informative_1h['rsi_14_1h'].empty and informative_1h['rsi_14_1h'].iloc[-1] > 70) |
                (not informative_1h.empty and 'bb_upper_1h' in informative_1h.columns and not informative_1h['bb_upper_1h'].empty and dataframe['close'] > informative_1h['bb_upper_1h'].iloc[-1]) |
                (not informative_1h.empty and 'obv_1h' in informative_1h.columns and not informative_1h['obv_1h'].empty and informative_1h['obv_1h'].iloc[-1] < informative_1h['obv_1h'].shift(1).iloc[-1])
            )
        )
        dataframe.loc[daytrade_exit, ['exit_long', 'exit_tag']] = (True, 'daytrade_exit')

        # SWING: RSI > 75, ADX opada, MACD signal slabosti
        swing_exit = (
            (dataframe['position_type'] == 'swing') &
            (
                (not informative_4h.empty and 'rsi_14_4h' in informative_4h.columns and not informative_4h['rsi_14_4h'].empty and informative_4h['rsi_14_4h'].iloc[-1] > 75) |
                (not informative_4h.empty and 'adx_14_4h' in informative_4h.columns and not informative_4h['adx_14_4h'].empty and informative_4h['adx_14_4h'].iloc[-1] < informative_4h['adx_14_4h'].shift(1).iloc[-1]) |
                (dataframe['macd'] < dataframe['macd_signal'])
            )
        )
        dataframe.loc[swing_exit, ['exit_long', 'exit_tag']] = (True, 'swing_exit')

        # LONG: RSI > 80, pad trenda, price ispod EMA200, obv pada
        long_exit = (
            (dataframe['position_type'] == 'long') &
            (
                (not informative_1d.empty and 'rsi_14_1d' in informative_1d.columns and not informative_1d['rsi_14_1d'].empty and informative_1d['rsi_14_1d'].iloc[-1] > 80) |
                (not informative_1d.empty and 'ema_200_1d' in informative_1d.columns and not informative_1d['ema_200_1d'].empty and dataframe['close'] < informative_1d['ema_200_1d'].iloc[-1]) |
                (dataframe['macd'] < dataframe['macd_signal']) |
                (not informative_1d.empty and 'obv_1d' in informative_1d.columns and not informative_1d['obv_1d'].empty and informative_1d['obv_1d'].iloc[-1] < informative_1d['obv_1d'].shift(1).iloc[-1])
            )
        )
        dataframe.loc[long_exit, ['exit_long', 'exit_tag']] = (True, 'long_exit')

        return dataframe
'''
'''
    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime, current_rate: float,
                    current_profit: float, metadata: dict, **kwargs):
        print(f"Poziva se custom_exit za par: {pair}, profit: {current_profit}")
        print(f"Tip metadata: {type(metadata)}, Sadržaj metadata: {metadata}")
        print(f"Dodatni argumenti (kwargs): {kwargs}")
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
        if (not informative_1h.empty and 'rsi_14_1h' in informative_1h.columns and not informative_1h['rsi_14_1h'].empty and informative_1h['rsi_14_1h'].iloc[-1] < 30) and \
        (not informative_1h.empty and 'ema_50_1h' in informative_1h.columns and 'ema_200_1h' in informative_1h.columns and not informative_1h['ema_50_1h'].empty and not informative_1h['ema_200_1h'].empty and informative_1h['ema_50_1h'].iloc[-1] < informative_1h['ema_200_1h'].iloc[-1]):
            return "rsi_bear_exit"

        # 3. MACD histogram pada + RSI slabost
        if (not informative_1h.empty and 'macd_histogram_1h' in informative_1h.columns and not informative_1h['macd_histogram_1h'].empty and informative_1h['macd_histogram_1h'].iloc[-1] < 0) and \
        (not informative_1h.empty and 'rsi_14_1h' in informative_1h.columns and not informative_1h['rsi_14_1h'].empty and informative_1h['rsi_14_1h'].iloc[-1] < 40):
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
        if current_profit > 0.04 and (not informative_1h.empty and 'rsi_14_1h' in informative_1h.columns and not informative_1h['rsi_14_1h'].empty and informative_1h['rsi_14_1h'].iloc[-1] > 75):
            return "take_profit_rsi_peak"

        # 7. RSI pada sa visokih vrednosti + CCI divergencija
        # Pretpostavljam da imate 'cci' u vašem osnovnom dataframe-u
        if last_candle['rsi_14_1h'] < 70 and last_candle['cci'] < 100 and current_profit > 0.03:
            return "momentum_loss_exit"

        # ===== POZICIJE SA ZADRŽAVANJEM =====

        # 8. Zadrži poziciju ako je u uzlaznom trendu
        if trade.tag in ["swing", "long"] and \
        (not informative_1h.empty and 'ema_50_1h' in informative_1h.columns and 'ema_200_1h' in informative_1h.columns and not informative_1h['ema_50_1h'].empty and not informative_1h['ema_200_1h'].empty and informative_1h['ema_50_1h'].iloc[-1] > informative_1h['ema_200_1h'].iloc[-1]) and \
        (not informative_1h.empty and 'rsi_14_1h' in informative_1h.columns and not informative_1h['rsi_14_1h'].empty and informative_1h['rsi_14_1h'].iloc[-1] > 55):
            return None  # ne izlazi

        # 9. Zadrži daytrade ako RSI i momentum još drže
        if trade.tag in ["daytrade", "position"] and \
        current_profit > 0.015 and (not informative_1h.empty and 'rsi_14_1h' in informative_1h.columns and not informative_1h['rsi_14_1h'].empty and informative_1h['rsi_14_1h'].iloc[-1] > 50):
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
            if (not informative_4h.empty and 'rsi_14_4h' in informative_4h.columns and not informative_4h['rsi_14_4h'].empty and informative_4h['rsi_14_4h'].iloc[-1] < 55) and \
            (not informative_4h.empty and 'macd_histogram_4h' in informative_4h.columns and not informative_4h['macd_histogram_4h'].empty and informative_4h['macd_histogram_4h'].iloc[-1] < 0):
                trade.entry_tag = 'daytrade'
                return "Switched swing -> daytrade"

        # ===== LONG -> SWING =====
        if current_type == 'long':
            if (not informative_1d.empty and 'rsi_14_1d' in informative_1d.columns and not informative_1d['rsi_14_1d'].empty and informative_1d['rsi_14_1d'].iloc[-1] < 60) or \
            (not informative_1d.empty and 'ema_50_1d' in informative_1d.columns and 'ema_200_1d' in informative_1d.columns and not informative_1d['ema_50_1d'].empty and not informative_1d['ema_200_1d'].empty and informative_1d['ema_50_1d'].iloc[-1] < informative_1d['ema_200_1d'].iloc[-1]):
                trade.entry_tag = 'swing'
                return "Switched long -> swing"

        # ===== SCALP -> POSITION =====
        if current_type == 'scalp':
            if last['rsi_14'] < 50 and (not informative_1h.empty and 'macd_histogram_1h' in informative_1h.columns and not informative_1h['macd_histogram_1h'].empty and informative_1h['macd_histogram_1h'].iloc[-1] < 0):
                trade.entry_tag = 'position'
                return "Switched scalp -> position"
        return None  # No change
'''
