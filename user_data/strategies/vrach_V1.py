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
        # === Timeframe 5m ===
        dataframe['sma_20_5m'] = ta.SMA(dataframe['close'], timeperiod=20)
        dataframe['ema_20_5m'] = ta.EMA(dataframe['close'], timeperiod=20)
        dataframe['wma_20_5m'] = ta.WMA(dataframe['close'], timeperiod=20)
        dataframe['rsi_14_5m'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['cci_20_5m'] = ta.CCI(dataframe, timeperiod=20)
        dataframe['mfi_14_5m'] = ta.MFI(dataframe, timeperiod=14)
        dataframe['adx_14_5m'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['+di_5m'] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe['-di_5m'] = ta.MINUS_DI(dataframe, timeperiod=14)
        dataframe['atr_14_5m'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['roc_10_5m'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_5m'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_5m'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb = ta.BBANDS(dataframe, timeperiod=10, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_5m'] = bb['upperband']
        dataframe['bb_middle_5m'] = bb['middleband']
        dataframe['bb_lower_5m'] = bb['lowerband']

        # === Timeframe 15m ===
        dataframe['sma_30_15m'] = ta.SMA(dataframe['close'], timeperiod=30)
        dataframe['ema_25_15m'] = ta.EMA(dataframe['close'], timeperiod=25)
        dataframe['wma_25_15m'] = ta.WMA(dataframe['close'], timeperiod=25)
        dataframe['rsi_14_15m'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['cci_20_15m'] = ta.CCI(dataframe, timeperiod=20)
        dataframe['mfi_14_15m'] = ta.MFI(dataframe, timeperiod=14)
        dataframe['adx_14_15m'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['+di_15m'] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe['-di_15m'] = ta.MINUS_DI(dataframe, timeperiod=14)
        dataframe['atr_14_15m'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['roc_10_15m'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_15m'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_15m'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb = ta.BBANDS(dataframe, timeperiod=15, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_15m'] = bb['upperband']
        dataframe['bb_middle_15m'] = bb['middleband']
        dataframe['bb_lower_15m'] = bb['lowerband']

        # === Timeframe 30m ===
        dataframe['sma_40_30m'] = ta.SMA(dataframe['close'], timeperiod=40)
        dataframe['ema_30_30m'] = ta.EMA(dataframe['close'], timeperiod=30)
        dataframe['wma_30_30m'] = ta.WMA(dataframe['close'], timeperiod=30)
        dataframe['rsi_12_30m'] = ta.RSI(dataframe['close'], timeperiod=12)
        dataframe['cci_20_30m'] = ta.CCI(dataframe, timeperiod=20)
        dataframe['mfi_14_30m'] = ta.MFI(dataframe, timeperiod=14)
        dataframe['adx_14_30m'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['+di_30m'] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe['-di_30m'] = ta.MINUS_DI(dataframe, timeperiod=14)
        dataframe['atr_14_30m'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['roc_10_30m'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_30m'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_30m'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_30m'] = bb['upperband']
        dataframe['bb_middle_30m'] = bb['middleband']
        dataframe['bb_lower_30m'] = bb['lowerband']

        # 1h timeframe
        dataframe['sma_50_1h'] = ta.SMA(dataframe['close'], timeperiod=50)
        dataframe['ema_40_1h'] = ta.EMA(dataframe['close'], timeperiod=40)
        dataframe['wma_35_1h'] = ta.WMA(dataframe['close'], timeperiod=35)
        dataframe['rsi_10_1h'] = ta.RSI(dataframe['close'], timeperiod=10)
        dataframe['cci_14_1h'] = ta.CCI(dataframe, timeperiod=14)
        dataframe['mfi_14_1h'] = ta.MFI(dataframe, timeperiod=14)
        dataframe['adx_14_1h'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['+di_1h'] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe['-di_1h'] = ta.MINUS_DI(dataframe, timeperiod=14)
        dataframe['atr_14_1h'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['roc_10_1h'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_1h'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_1h'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb_1h = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_1h'] = bb_1h['upperband']
        dataframe['bb_middle_1h'] = bb_1h['middleband']
        dataframe['bb_lower_1h'] = bb_1h['lowerband']

        # 4h timeframe
        dataframe['sma_60_4h'] = ta.SMA(dataframe['close'], timeperiod=60)
        dataframe['ema_50_4h'] = ta.EMA(dataframe['close'], timeperiod=50)
        dataframe['wma_45_4h'] = ta.WMA(dataframe['close'], timeperiod=45)
        dataframe['rsi_9_4h'] = ta.RSI(dataframe['close'], timeperiod=9)
        dataframe['cci_14_4h'] = ta.CCI(dataframe, timeperiod=14)
        dataframe['mfi_10_4h'] = ta.MFI(dataframe, timeperiod=10)
        dataframe['adx_10_4h'] = ta.ADX(dataframe, timeperiod=10)
        dataframe['+di_4h'] = ta.PLUS_DI(dataframe, timeperiod=10)
        dataframe['-di_4h'] = ta.MINUS_DI(dataframe, timeperiod=10)
        dataframe['atr_14_4h'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['roc_10_4h'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_4h'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_4h'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb_4h = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_4h'] = bb_4h['upperband']
        dataframe['bb_middle_4h'] = bb_4h['middleband']
        dataframe['bb_lower_4h'] = bb_4h['lowerband']

        # 8h timeframe
        dataframe['sma_70_8h'] = ta.SMA(dataframe['close'], timeperiod=70)
        dataframe['ema_60_8h'] = ta.EMA(dataframe['close'], timeperiod=60)
        dataframe['wma_55_8h'] = ta.WMA(dataframe['close'], timeperiod=55)
        dataframe['rsi_8_8h'] = ta.RSI(dataframe['close'], timeperiod=8)
        dataframe['cci_14_8h'] = ta.CCI(dataframe, timeperiod=14)
        dataframe['mfi_10_8h'] = ta.MFI(dataframe, timeperiod=10)
        dataframe['adx_10_8h'] = ta.ADX(dataframe, timeperiod=10)
        dataframe['+di_8h'] = ta.PLUS_DI(dataframe, timeperiod=10)
        dataframe['-di_8h'] = ta.MINUS_DI(dataframe, timeperiod=10)
        dataframe['atr_10_8h'] = ta.ATR(dataframe, timeperiod=10)
        dataframe['roc_10_8h'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_8h'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_8h'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb_8h = ta.BBANDS(dataframe, timeperiod=25, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_8h'] = bb_8h['upperband']
        dataframe['bb_middle_8h'] = bb_8h['middleband']
        dataframe['bb_lower_8h'] = bb_8h['lowerband']

        # 12h timeframe
        dataframe['sma_80_12h'] = ta.SMA(dataframe['close'], timeperiod=80)
        dataframe['ema_70_12h'] = ta.EMA(dataframe['close'], timeperiod=70)
        dataframe['wma_65_12h'] = ta.WMA(dataframe['close'], timeperiod=65)
        dataframe['rsi_7_12h'] = ta.RSI(dataframe['close'], timeperiod=7)
        dataframe['cci_10_12h'] = ta.CCI(dataframe, timeperiod=10)
        dataframe['mfi_10_12h'] = ta.MFI(dataframe, timeperiod=10)
        dataframe['adx_10_12h'] = ta.ADX(dataframe, timeperiod=10)
        dataframe['+di_12h'] = ta.PLUS_DI(dataframe, timeperiod=10)
        dataframe['-di_12h'] = ta.MINUS_DI(dataframe, timeperiod=10)
        dataframe['atr_10_12h'] = ta.ATR(dataframe, timeperiod=10)
        dataframe['roc_10_12h'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_12h'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_12h'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb_12h = ta.BBANDS(dataframe, timeperiod=30, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_12h'] = bb_12h['upperband']
        dataframe['bb_middle_12h'] = bb_12h['middleband']
        dataframe['bb_lower_12h'] = bb_12h['lowerband']

        # 1d timeframe
        dataframe['sma_100_1d'] = ta.SMA(dataframe['close'], timeperiod=100)
        dataframe['ema_90_1d'] = ta.EMA(dataframe['close'], timeperiod=90)
        dataframe['wma_80_1d'] = ta.WMA(dataframe['close'], timeperiod=80)
        dataframe['rsi_6_1d'] = ta.RSI(dataframe['close'], timeperiod=6)
        dataframe['cci_10_1d'] = ta.CCI(dataframe, timeperiod=10)
        dataframe['mfi_10_1d'] = ta.MFI(dataframe, timeperiod=10)
        dataframe['adx_10_1d'] = ta.ADX(dataframe, timeperiod=10)
        dataframe['+di_1d'] = ta.PLUS_DI(dataframe, timeperiod=10)
        dataframe['-di_1d'] = ta.MINUS_DI(dataframe, timeperiod=10)
        dataframe['atr_10_1d'] = ta.ATR(dataframe, timeperiod=10)
        dataframe['roc_10_1d'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_1d'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_1d'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb_1d = ta.BBANDS(dataframe, timeperiod=35, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_1d'] = bb_1d['upperband']
        dataframe['bb_middle_1d'] = bb_1d['middleband']
        dataframe['bb_lower_1d'] = bb_1d['lowerband']

        # 1w timeframe
        dataframe['sma_200_1w'] = ta.SMA(dataframe['close'], timeperiod=200)
        dataframe['ema_150_1w'] = ta.EMA(dataframe['close'], timeperiod=150)
        dataframe['wma_120_1w'] = ta.WMA(dataframe['close'], timeperiod=120)
        dataframe['rsi_5_1w'] = ta.RSI(dataframe['close'], timeperiod=5)
        dataframe['cci_10_1w'] = ta.CCI(dataframe, timeperiod=10)
        dataframe['mfi_10_1w'] = ta.MFI(dataframe, timeperiod=10)
        dataframe['adx_10_1w'] = ta.ADX(dataframe, timeperiod=10)
        dataframe['+di_1w'] = ta.PLUS_DI(dataframe, timeperiod=10)
        dataframe['-di_1w'] = ta.MINUS_DI(dataframe, timeperiod=10)
        dataframe['atr_10_1w'] = ta.ATR(dataframe, timeperiod=10)
        dataframe['roc_10_1w'] = ta.ROC(dataframe['close'], timeperiod=10)
        dataframe['tema_20_1w'] = ta.TEMA(dataframe['close'], timeperiod=20)
        dataframe['kama_10_1w'] = ta.KAMA(dataframe['close'], timeperiod=10)
        bb_1w = ta.BBANDS(dataframe, timeperiod=50, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_upper_1w'] = bb_1w['upperband']
        dataframe['bb_middle_1w'] = bb_1w['middleband']
        dataframe['bb_lower_1w'] = bb_1w['lowerband']

        # === Statički indikatori izvan vremenskih okvira ===
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        dataframe['obv'] = ta.OBV(dataframe)

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
