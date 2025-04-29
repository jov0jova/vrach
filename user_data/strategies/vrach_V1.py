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
    informative_timeframes = ['5m','15m','30m','1h','4h','8h','12h','1d','7d']
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
        # Simple Moving Average (SMA)
        dataframe['sma_50'] = ta_lib.SMA(dataframe['close'], timeperiod=50)
        
        # Exponential Moving Average (EMA)
        dataframe['ema_50'] = ta_lib.EMA(dataframe['close'], timeperiod=50)
        
        # Weighted Moving Average (WMA)
        dataframe['wma_50'] = ta_lib.WMA(dataframe['close'], timeperiod=50)

        # 200-period Simple Moving Average (SMA 200)
        dataframe['sma_200'] = ta_lib.SMA(dataframe['close'], timeperiod=200)

        # 200-period Exponential Moving Average (EMA 200)
        dataframe['ema_200'] = ta_lib.EMA(dataframe['close'], timeperiod=200)

        # 200-period Weighted Moving Average (WMA 200)
        dataframe['wma_200'] = ta_lib.WMA(dataframe['close'], timeperiod=200)

        # Relative Strength Index (RSI)
        dataframe['rsi_14'] = ta_lib.RSI(dataframe['close'], timeperiod=14)

        # MACD and its components
        macd = ta_lib.MACD(dataframe['close'])
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # Bollinger Bands
        bb = ta.bbands(dataframe['close'], length=20, std=2)
        dataframe['bb_upper'] = bb['BBU_20_2.0']
        dataframe['bb_middle'] = bb['BBM_20_2.0']
        dataframe['bb_lower'] = bb['BBL_20_2.0']

        # Commodity Channel Index (CCI)
        dataframe['cci_20'] = ta_lib.CCI(dataframe, timeperiod=20)

        # Money Flow Index (MFI)
        dataframe['mfi_14'] = ta_lib.MFI(dataframe, timeperiod=14)

        # Average True Range (ATR)
        dataframe['atr_14'] = ta_lib.ATR(dataframe, timeperiod=14)

        # Average Directional Index (ADX) and Directional Indicators
        dataframe['adx_14'] = ta_lib.ADX(dataframe, timeperiod=14)
        dataframe['+di'] = ta_lib.PLUS_DI(dataframe, timeperiod=14)
        dataframe['-di'] = ta_lib.MINUS_DI(dataframe, timeperiod=14)

        # Stochastic Oscillator
        stoch = ta_lib.STOCH(dataframe)
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']

        # Stochastic RSI
        stoch_rsi = ta.stochrsi(dataframe['close'])
        dataframe['stoch_rsi_k'] = stoch_rsi['STOCHRSIk_14_14_3_3']
        dataframe['stoch_rsi_d'] = stoch_rsi['STOCHRSId_14_14_3_3']

        # On-Balance Volume (OBV)
        dataframe['obv'] = ta_lib.OBV(dataframe)

        # Rate of Change (ROC)
        dataframe['roc_14'] = ta_lib.ROC(dataframe['close'], timeperiod=14)

        # Triple Exponential Moving Average (TEMA)
        dataframe['tema_20'] = ta_lib.TEMA(dataframe['close'], timeperiod=20)

        # TRIX (Triple Exponential Average)
        dataframe['trix'] = ta.trix(dataframe['close'])

        # Kaufman's Adaptive Moving Average (KAMA)
        dataframe['kama'] = ta_lib.KAMA(dataframe['close'], timeperiod=10)

        # VWAP (Volume Weighted Average Price) - used on minute timeframes
        if metadata.get('timeframe') in ['5m', '15m', '30m', '1h']:
            vwap = ta.vwap(dataframe['high'], dataframe['low'], dataframe['close'], dataframe['volume'])
            dataframe['vwap'] = vwap

        # Ichimoku Cloud components
        ichimoku = ta.ichimoku(dataframe['high'], dataframe['low'])
        dataframe['ichi_base'] = ichimoku['ISA_9']
        dataframe['ichi_conversion'] = ichimoku['ISB_26']
        dataframe['ichi_leading_span_a'] = ichimoku['ITS_9']
        dataframe['ichi_leading_span_b'] = ichimoku['IKS_26']

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
