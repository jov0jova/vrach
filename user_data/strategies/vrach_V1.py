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

        timeframes = ['5m', '15m', '30m', '1h', '4h', '8h', '12h', '1d', '1w']
        periods = {
            'rsi':     {'5m':14, '15m':14, '30m':12, '1h':10, '4h':9, '8h':8, '12h':7, '1d':6, '1w':5},
            'sma':     {'5m':20, '15m':30, '30m':40, '1h':50, '4h':60, '8h':70, '12h':80, '1d':100, '1w':200},
            'ema':     {'5m':20, '15m':25, '30m':30, '1h':40, '4h':50, '8h':60, '12h':70, '1d':90, '1w':150},
            'wma':     {'5m':20, '15m':25, '30m':30, '1h':35, '4h':45, '8h':55, '12h':65, '1d':80, '1w':120},
            'cci':     {'5m':20, '15m':20, '30m':20, '1h':14, '4h':14, '8h':14, '12h':10, '1d':10, '1w':10},
            'mfi':     {'5m':14, '15m':14, '30m':14, '1h':14, '4h':10, '8h':10, '12h':10, '1d':10, '1w':10},
            'adx':     {'5m':14, '15m':14, '30m':14, '1h':14, '4h':10, '8h':10, '12h':10, '1d':10, '1w':10},
            'atr':     {'5m':14, '15m':14, '30m':14, '1h':14, '4h':14, '8h':10, '12h':10, '1d':10, '1w':10},
            'roc':     {'5m':10, '15m':10, '30m':10, '1h':10, '4h':10, '8h':10, '12h':10, '1d':10, '1w':10},
            'tema':    {'5m':20, '15m':20, '30m':20, '1h':20, '4h':20, '8h':20, '12h':20, '1d':20, '1w':20},
            'kama':    {'5m':10, '15m':10, '30m':10, '1h':10, '4h':10, '8h':10, '12h':10, '1d':10, '1w':10},
            'bbands':    {'5m':10, '15m':15, '30m':20, '1h':20, '4h':20, '8h':25, '12h':30, '1d':35, '1w':50},
        }

        for tf in timeframes:
            rsi_p = periods['rsi'][tf]
            sma_p = periods['sma'][tf]
            ema_p = periods['ema'][tf]
            wma_p = periods['wma'][tf]
            cci_p = periods['cci'][tf]
            mfi_p = periods['mfi'][tf]
            adx_p = periods['adx'][tf]
            atr_p = periods['atr'][tf]
            roc_p = periods['roc'][tf]
            tema_p = periods['tema'][tf]
            kama_p = periods['kama'][tf]
            bbands_p = periods['bbands'][tf]

            # SMA, EMA, WMA
            dataframe[f'sma_{sma_p}_{tf}'] = ta.SMA(dataframe['close'], timeperiod=sma_p)
            dataframe[f'ema_{ema_p}_{tf}'] = ta.EMA(dataframe['close'], timeperiod=ema_p)
            dataframe[f'wma_{wma_p}_{tf}'] = ta.WMA(dataframe['close'], timeperiod=wma_p)

            # RSI
            dataframe[f'rsi_{rsi_p}_{tf}'] = ta.RSI(dataframe['close'], timeperiod=rsi_p)

            # CCI
            dataframe[f'cci_{cci_p}_{tf}'] = ta.CCI(dataframe, timeperiod=cci_p)

            # MFI
            dataframe[f'mfi_{mfi_p}_{tf}'] = ta.MFI(dataframe, timeperiod=mfi_p)

            # ADX +DI -DI
            dataframe[f'adx_{adx_p}_{tf}'] = ta.ADX(dataframe, timeperiod=adx_p)
            dataframe[f'+di_{tf}'] = ta.PLUS_DI(dataframe, timeperiod=adx_p)
            dataframe[f'-di_{tf}'] = ta.MINUS_DI(dataframe, timeperiod=adx_p)

            # ATR
            dataframe[f'atr_{atr_p}_{tf}'] = ta.ATR(dataframe, timeperiod=atr_p)

            # ROC
            dataframe[f'roc_{roc_p}_{tf}'] = ta.ROC(dataframe['close'], timeperiod=roc_p)

            # TEMA
            dataframe[f'tema_{tema_p}_{tf}'] = ta.TEMA(dataframe['close'], timeperiod=tema_p)

            # KAMA
            dataframe[f'kama_{kama_p}_{tf}'] = ta.KAMA(dataframe['close'], timeperiod=kama_p)

            # Bollinger Bands (20, 2)
            bb = ta.BBANDS(dataframe['close'], timeperiod=bbands_p, nbdevup=2.0, nbdevdn=2.0, matype=0)
            dataframe[f'bb_upper_{tf}'] = bb['upperband']
            dataframe[f'bb_middle_{tf}'] = bb['middleband']
            dataframe[f'bb_lower_{tf}'] = bb['lowerband']
        
        # Indikatori izvan petlje (računaju se samo jednom)
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        dataframe['obv'] = ta.OBV(dataframe)
        dataframe['trix'] = ta.trix(dataframe['close'])

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe

        dataframe['enter_long'] = False
        dataframe['position_type'] = None

        # ✅ SCALP TRADE — RSI oversold + BB touch + high volatility
        scalp_cond = (
            (dataframe['rsi_14_5m'] < 30) &
            (dataframe['close'] < dataframe['bb_lower_5m']) &
            (dataframe['atr_14_5m'] > dataframe['atr_14_5m'].rolling(20).mean()) &
            (dataframe['volume'] > 0)
        )

        dataframe.loc[scalp_cond, 'enter_long'] = True
        dataframe.loc[scalp_cond, 'position_type'] = 'scalp'

        # ✅ POSITION TRADE — EMA50 < EMA200 + RSI recovery + MACD crossover
        position_cond = (
            (dataframe['ema_50_1h'] < dataframe['ema_200_1h']) &
            (dataframe['rsi_14_1h'] > 30) & (dataframe['rsi_14_1h'] < 50) &
            (dataframe['macd'] > dataframe['macdsignal']) &
            (dataframe['volume'] > 0)
        )

        dataframe.loc[position_cond, 'enter_long'] = True
        dataframe.loc[position_cond, 'position_type'] = 'position'

        # ✅ DAYTRADE — Trend reversal: RSI < 40 + BB lower bounce + MACD up + OBV rising
        daytrade_cond = (
            (dataframe['rsi_14_1h'] < 40) &
            (dataframe['close'] <= dataframe['bb_lower_1h']) &
            (dataframe['macd'] > dataframe['macdsignal']) &
            (dataframe['obv_1h'] > dataframe['obv_1h'].shift(1)) &
            (dataframe['volume'] > 0)
        )

        dataframe.loc[daytrade_cond, 'enter_long'] = True
        dataframe.loc[daytrade_cond, 'position_type'] = 'daytrade'

        # ✅ SWING TRADE — EMA200 slope up + ADX > 25 + MACD > 0 + RSI 40–60
        swing_cond = (
            (dataframe['ema_200_4h'] > dataframe['ema_200_4h'].shift(1)) &
            (dataframe['adx_14_4h'] > 25) &
            (dataframe['macd'] > 0) &
            (dataframe['rsi_14_4h'] > 40) & (dataframe['rsi_14_4h'] < 60) &
            (dataframe['volume'] > 0)
        )

        dataframe.loc[swing_cond, 'enter_long'] = True
        dataframe.loc[swing_cond, 'position_type'] = 'swing'

        # ✅ LONG TERM — EMA200 uptrend + RSI breakout + MACD > 0 + Price above BB middle
        long_cond = (
            (dataframe['ema_200_1d'] > dataframe['ema_200_1d'].shift(1)) &
            (dataframe['rsi_14_1d'] > 50) &
            (dataframe['macd'] > dataframe['macdsignal']) &
            (dataframe['close'] > dataframe['bb_middle_1d']) &
            (dataframe['volume'] > 0)
        )

        dataframe.loc[long_cond, 'enter_long'] = True
        dataframe.loc[long_cond, 'position_type'] = 'long'

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe

        dataframe['exit_long'] = False

        # SCALP: Brzi profiti — izlazi kad RSI pređe 70 ili dođe do BB gornje
        scalp_exit = (
            (dataframe['position_type'] == 'scalp') &
            (
                (dataframe['rsi_14_5m'] > 70) |
                (dataframe['close'] > dataframe['bb_upper_5m']) |
                (dataframe['macd'] < dataframe['macdsignal'])  # gubi momentum
            )
        )
        dataframe.loc[scalp_exit, 'exit_long'] = True

        # POSITION: RSI previše visok, MACD se obrće, pad volumena
        position_exit = (
            (dataframe['position_type'] == 'position') &
            (
                (dataframe['rsi_14_1h'] > 65) &
                (dataframe['macd'] < dataframe['macdsignal']) |
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
                (dataframe['macd'] < dataframe['macdsignal'])
            )
        )
        dataframe.loc[swing_exit, 'exit_long'] = True

        # LONG: RSI > 80, pad trenda, price ispod EMA200, obv pada
        long_exit = (
            (dataframe['position_type'] == 'long') &
            (
                (dataframe['rsi_14_1d'] > 80) |
                (dataframe['close'] < dataframe['ema_200_1d']) |
                (dataframe['macd'] < dataframe['macdsignal']) |
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

        last_candle = dataframe.iloc[-1]

            # ===== RISK MANAGEMENT =====

        # 1. Hitni izlaz ako je gubitak prevelik
        if current_profit < -0.08:
            return "emergency_loss_cut"

        # 2. RSI i trend pokazuju pad - izađi
        if last_candle['rsi'] < 30 and last_candle['ema50'] < last_candle['ema200']:
            return "rsi_bear_exit"

        # 3. MACD histogram pada + RSI slabost
        if last_candle['macdhist'] < 0 and last_candle['rsi'] < 40:
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
        if current_profit > 0.04 and last_candle['rsi'] > 75:
            return "take_profit_rsi_peak"

        # 7. RSI pada sa visokih vrednosti + CCI divergencija
        if last_candle['rsi'] < 70 and last_candle['cci'] < 100 and current_profit > 0.03:
            return "momentum_loss_exit"

        # ===== POZICIJE SA ZADRŽAVANJEM =====

        # 8. Zadrži poziciju ako je u uzlaznom trendu
        if trade.tag in ["swing", "long"] and \
        last_candle['ema50'] > last_candle['ema200'] and \
        last_candle['rsi'] > 55:
            return None  # ne izlazi

        # 9. Zadrži daytrade ako RSI i momentum još drže
        if trade.tag in ["daytrade", "position"] and \
        current_profit > 0.015 and last_candle['rsi'] > 50:
            return None  # zadrži

        # 10. Scalp - brzi izlaz pri malom profitu
        if trade.tag == "scalp" and current_profit > 0.012:
            return "quick_scalp_exit"

        return None  # default: ne menjaj ništa
    
    def adjust_trade_position_type(self, trade: 'Trade', dataframe: DataFrame):
        last = dataframe.iloc[-1]
        current_type = trade.entry_tag

        # Swing slabi, prebaci ga u daytrade
        if current_type == 'swing':
            if last['rsi_14_4h'] < 55 and last['macd'] < last['macdsignal']:
                trade.entry_tag = 'daytrade'
                return "Switched swing -> daytrade"

        # Long gubi snagu, prebaci ga u swing
        if current_type == 'long':
            if last['rsi_14_1d'] < 60 or last['ema_50_1d'] < last['ema_200_1d']:
                trade.entry_tag = 'swing'
                return "Switched long -> swing"

        # Ako scalp nije izašao ali momentum opada, prebaci ga u position
        if current_type == 'scalp':
            if last['rsi_14_5m'] < 50 and last['macd'] < last['macdsignal']:
                trade.entry_tag = 'position'
                return "Switched scalp -> position"

        return None  # Nema promene
