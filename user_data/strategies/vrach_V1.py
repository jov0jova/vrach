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

# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Dict, Optional, Union, Tuple

from freqtrade.strategy import (
    IStrategy,
    Trade, 
    Order,
    PairLocks,
    informative,  # @informative decorator
    # Hyperopt Parameters
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    RealParameter,
    # timeframe helpers
    timeframe_to_minutes,
    timeframe_to_next_date,
    timeframe_to_prev_date,
    # Strategy helper functions
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
from technical import qtpylib


class Vrach_Ultimate_PRO(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '5m'

    inf_timeframes = ['1h', '4h', '1d']
    
    minimal_roi = {}
    stoploss = -0.99
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True
    use_custom_stoploss = False
    can_short = False
    process_only_new_candles = True
    
    startup_candle_count = 800
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
        
        informative_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        informative_4h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='4h')
        informative_1d = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1d')

        'OVDE IDU INFO METRIKE'

        informative_1h['ema_7'] = ta.EMA(dataframe, timeperiod=7)

        dataframe = merge_informative_pair(dataframe, informative, self.timeframe, inf_tf, ffill=True)
        '''
        ////////////////////////////////////////////////////////////////////////////////////////////////////
        //                                                                                                //
        //       ____                      __                  _____  __              __ _                //
        //      / __ \ _   __ ___   _____ / /____ _ ____      / ___/ / /_ __  __ ____/ /(_)___   _____    //
        //     / / / /| | / // _ \ / ___// // __ `// __ \     \__ \ / __// / / // __  // // _ \ / ___/    //
        //    / /_/ / | |/ //  __// /   / // /_/ // /_/ /    ___/ // /_ / /_/ // /_/ // //  __/(__  )     //
        //    \____/  |___/ \___//_/   /_/ \__,_// .___/    /____/ \__/ \__,_/ \__,_//_/ \___//____/      //
        //                                      /_/                                                       //
        //                                                                                                //
        ////////////////////////////////////////////////////////////////////////////////////////////////////
        '''

        #BBANDS Bollinger Bands
        bb = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_lower'] = bb['lowerband']

        

        #DEMA Double Exponential Moving Average
        dataframe['dema_7'] = ta.DEMA(dataframe, timeperiod=7)
        dataframe['dema_25'] = ta.DEMA(dataframe, timeperiod=25)
        dataframe['dema_99'] = ta.DEMA(dataframe, timeperiod=99)
        dataframe['dema_200'] = ta.DEMA(dataframe, timeperiod=200)

        #EMA Exponential Moving Average
        dataframe['ema_7'] = ta.EMA(dataframe, timeperiod=7)
        dataframe['ema_25'] = ta.EMA(dataframe, timeperiod=25)
        dataframe['ema_99'] = ta.EMA(dataframe, timeperiod=99)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)

        #FEMA Fibonacci Exponenetial Moving Average
        dataframe['fema_3'] = ta.EMA(dataframe, timeperiod=3)
        dataframe['fema_5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['fema_8'] = ta.EMA(dataframe, timeperiod=8)
        dataframe['fema_13'] = ta.EMA(dataframe, timeperiod=13)
        dataframe['fema_21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['fema_34'] = ta.EMA(dataframe, timeperiod=34)
        dataframe['fema_55'] = ta.EMA(dataframe, timeperiod=55)
        dataframe['fema_89'] = ta.EMA(dataframe, timeperiod=89)
        dataframe['fema_144'] = ta.EMA(dataframe, timeperiod=144)
        dataframe['fema_233'] = ta.EMA(dataframe, timeperiod=233)

        #HT_TRENDLINE Hilbert Transform - Instantaneous Trendline
        dataframe['ht_trendline'] = ta.HT_TRENDLINE(dataframe)

        #KAMA Kaufman Adaptive Moving Average
        dataframe['kama_7'] = ta.KAMA(dataframe, timeperiod=7)
        dataframe['kama_25'] = ta.KAMA(dataframe, timeperiod=25)
        dataframe['kama_99'] = ta.KAMA(dataframe, timeperiod=99)
        dataframe['kama_200'] = ta.KAMA(dataframe, timeperiod=200)

        #MA Moving average


        #MAMA MESA Adaptive Moving Average
        dataframe['mama'], dataframe['fama'] = ta.MAMA(dataframe)

        #MAVP Moving average with variable period


        #MIDPOINT MidPoint over period
        dataframe['midpoint_7'] = ta.MIDPOINT(dataframe, timeperiod=7)
        dataframe['midpoint_25'] = ta.MIDPOINT(dataframe, timeperiod=25)
        dataframe['midpoint_99'] = ta.MIDPOINT(dataframe, timeperiod=99)
        dataframe['midpoint_200'] = ta.MIDPOINT(dataframe, timeperiod=200)

        #MIDPRICE Midpoint Price over period
        dataframe['midprice_7'] = ta.MIDPRICE(dataframe, timeperiod=7)
        dataframe['midprice_25'] = ta.MIDPRICE(dataframe, timeperiod=25)
        dataframe['midprice_99'] = ta.MIDPRICE(dataframe, timeperiod=99)
        dataframe['midprice_200'] = ta.MIDPRICE(dataframe, timeperiod=200)
        
        #SAR Parabolic SAR
        dataframe['sar'] = ta.SAR(dataframe)

        #SAREXT Parabolic SAR - Extended
        dataframe['sarext'] = ta.SAREXT(dataframe)

        #SMA Simple Moving Average
        dataframe['sma_7'] = ta.SMA(dataframe, timeperiod=7)
        dataframe['sma_25'] = ta.SMA(dataframe, timeperiod=25)
        dataframe['sma_99'] = ta.SMA(dataframe, timeperiod=99)
        dataframe['sma_200'] = ta.SMA(dataframe, timeperiod=200)

        #T3 Triple Exponential Moving Average (T3)
        dataframe['t3_7'] = ta.T3(dataframe, timeperiod=7)
        dataframe['t3_25'] = ta.T3(dataframe, timeperiod=25)
        dataframe['t3_99'] = ta.T3(dataframe, timeperiod=99)
        dataframe['t3_200'] = ta.T3(dataframe, timeperiod=200)

        #TEMA Triple Exponential Moving Average
        dataframe['tema_7'] = ta.TEMA(dataframe, timeperiod=20)
        dataframe['tema_25'] = ta.TEMA(dataframe, timeperiod=25)
        dataframe['tema_99'] = ta.TEMA(dataframe, timeperiod=99)
        dataframe['tema_200'] = ta.TEMA(dataframe, timeperiod=200)

        #TRIMA Triangular Moving Average
        dataframe['trima_7'] = ta.TRIMA(dataframe, timeperiod=7)
        dataframe['trima_25'] = ta.TRIMA(dataframe, timeperiod=25)
        dataframe['trima_99'] = ta.TRIMA(dataframe, timeperiod=99)
        dataframe['trima_200'] = ta.TRIMA(dataframe, timeperiod=200)

        #WMA Weighted Moving Average
        dataframe['wma_7'] = ta.WMA(dataframe, timeperiod=7)
        dataframe['wma_25'] = ta.WMA(dataframe, timeperiod=25)
        dataframe['wma_99'] = ta.WMA(dataframe, timeperiod=99)
        dataframe['wma_200'] = ta.WMA(dataframe, timeperiod=200)

        '''
        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        //                                                                                                                                        //
        //        __  ___                                __                         ____            __ _               __                         //
        //       /  |/  /____   ____ ___   ___   ____   / /_ __  __ ____ ___       /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____     //
        //      / /|_/ // __ \ / __ `__ \ / _ \ / __ \ / __// / / // __ `__ \      / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/     //
        //     / /  / // /_/ // / / / / //  __// / / // /_ / /_/ // / / / / /    _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )      //
        //    /_/  /_/ \____//_/ /_/ /_/ \___//_/ /_/ \__/ \__,_//_/ /_/ /_/    /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/       //
        //                                                                                                                                        //
        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        '''

        #ADX Average Directional Movement Index
        dataframe['adx'] = ta.ADX(dataframe)

        #ADXR Average Directional Movement Index Rating
        dataframe['adxr'] = ta.ADXR(dataframe)

        #APO Absolute Price Oscillator
        dataframe['apo'] = ta.APO(dataframe)

        #AROON Aroon

        #AROONOSC Aroon Oscillator
        dataframe['aroonosc'] = ta.AROONOSC(dataframe)

        #BOP Balance Of Power
        dataframe['bop'] = ta.BOP(dataframe)

        #CCI Commodity Channel Index
        dataframe['cci'] = ta.CCI(dataframe)

        #CMO Chande Momentum Oscillator
        dataframe['cmo'] = ta.CMO(dataframe)

        #DX Directional Movement Index
        dataframe['dx'] = ta.DX(dataframe)

        #MACD Moving Average Convergence/Divergence
        macd, macdsignal, macdhist = ta.MACD(dataframe)
        dataframe['macd'] = macd
        dataframe['macdsignal'] = macdsignal
        dataframe['macdhist'] = macdhist

        #MACDEXT MACD with controllable MA type
        dataframe['macdext'], _, _ = ta.MACDEXT(dataframe)
        
        #MACDFIX Moving Average Convergence/Divergence Fix 12/26
        dataframe['macdfix'], _, _ = ta.MACDFIX(dataframe)

        #MFI Money Flow Index
        dataframe['mfi'] = ta.MFI(dataframe)

        #MINUS_DI Minus Directional Indicator
        dataframe['minus_di'] = ta.MINUS_DI(dataframe)

        #MINUS_DM Minus Directional Movement
        dataframe['minus_dm'] = ta.MINUS_DM(dataframe)

        #MOM Momentum
        dataframe['mom'] = ta.MOM(dataframe)

        #PLUS_DI Plus Directional Indicator
        dataframe['plus_di'] = ta.PLUS_DI(dataframe)

        #PLUS_DM Plus Directional Movement
        dataframe['plus_dm'] = ta.PLUS_DM(dataframe)

        #PPO Percentage Price Oscillator
        dataframe['ppo'] = ta.PPO(dataframe)

        #ROC Rate of change : ((price/prevPrice)-1)*100
        dataframe['roc'] = ta.ROC(dataframe)

        #ROCP Rate of change Percentage: (price-prevPrice)/prevPrice
        dataframe['rocp'] = ta.ROCP(dataframe)

        #ROCR Rate of change ratio: (price/prevPrice)
        dataframe['rocr'] = ta.ROCR(dataframe)

        #ROCR100 Rate of change ratio 100 scale: (price/prevPrice)*100
        dataframe['rocr100'] = ta.ROCR100(dataframe)

        #RSI Relative Strength Index
        dataframe['rsi_3'] = ta.RSI(dataframe,timeperiod=3)
        dataframe['rsi_5'] = ta.RSI(dataframe,timeperiod=5)
        dataframe['rsi_8'] = ta.RSI(dataframe,timeperiod=8)
        dataframe['rsi_13'] = ta.RSI(dataframe,timeperiod=13)
        dataframe['rsi_21'] = ta.RSI(dataframe,timeperiod=21)
        dataframe['rsi_34'] = ta.RSI(dataframe,timeperiod=34)

        #STOCH Stochastic
        slowk, slowd = ta.STOCH(dataframe)
        dataframe['stoch_k'] = slowk
        dataframe['stoch_d'] = slowd

        #STOCHF Stochastic Fast
        fastk, fastd = ta.STOCHF(dataframe)
        dataframe['stochf_k'] = fastk
        dataframe['stochf_d'] = fastd
        
        #STOCHRSI Stochastic Relative Strength Index
        dataframe['stochrsi_k'], dataframe['stochrsi_d'] = ta.STOCHRSI(dataframe)

        #TRIX 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        dataframe['trix'] = ta.TRIX(dataframe)

        #ULTOSC Ultimate Oscillator
        dataframe['ultosc'] = ta.ULTOSC(dataframe)

        #WILLR Williams' %R
        dataframe['willr'] = ta.WILLR(dataframe)


        '''
        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        //                                                                                                                //
        //     _    __        __                             ____            __ _               __                        //
        //    | |  / /____   / /__  __ ____ ___   ___       /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____    //
        //    | | / // __ \ / // / / // __ `__ \ / _ \      / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/    //
        //    | |/ // /_/ // // /_/ // / / / / //  __/    _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )     //
        //    |___/ \____//_/ \__,_//_/ /_/ /_/ \___/    /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/      //
        //                                                                                                                //
        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        '''

        #AD Chaikin A/D Line
        dataframe['ad'] = ta.AD(dataframe)

        #ADOSC Chaikin A/D Oscillator
        dataframe['adosc'] = ta.ADOSC(dataframe)

        #OBV On Balance Volume
        dataframe['obv'] = ta.OBV(dataframe)


        '''
        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        //                                                                                                                        //
        //     _    __        __        __   _  __ _  __             ____            __ _               __                        //
        //    | |  / /____   / /____ _ / /_ (_)/ /(_)/ /_ __  __    /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____    //
        //    | | / // __ \ / // __ `// __// // // // __// / / /    / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/    //
        //    | |/ // /_/ // // /_/ // /_ / // // // /_ / /_/ /   _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )     //
        //    |___/ \____//_/ \__,_/ \__//_//_//_/ \__/ \__, /   /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/      //
        //                                             /____/                                                                     //
        //                                                                                                                        //
        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        '''

        #ATR Average True Range
        dataframe['atr'] = ta.ATR(dataframe)

        #NATR Normalized Average True Range
        dataframe['natr'] = ta.NATR(dataframe)

        #TRANGE True Range
        dataframe['trange'] = ta.TRANGE(dataframe)


        '''
        //////////////////////////////////////////////////////////////////////////////////////////////////////////
        //                                                                                                      //
        //        ____         _                ______                           ____                           //
        //       / __ \ _____ (_)_____ ___     /_  __/_____ ____ _ ____   _____ / __/____   _____ ____ ___      //
        //      / /_/ // ___// // ___// _ \     / /  / ___// __ `// __ \ / ___// /_ / __ \ / ___// __ `__ \     //
        //     / ____// /   / // /__ /  __/    / /  / /   / /_/ // / / /(__  )/ __// /_/ // /   / / / / / /     //
        //    /_/    /_/   /_/ \___/ \___/    /_/  /_/    \__,_//_/ /_//____//_/   \____//_/   /_/ /_/ /_/      //
        //                                                                                                      //
        //////////////////////////////////////////////////////////////////////////////////////////////////////////
        '''

        #AVGPRICE Average Price
        dataframe['avgprice'] = ta.AVGPRICE(dataframe)

        #MEDPRICE Median Price
        dataframe['medprice'] = ta.MEDPRICE(dataframe)

        #TYPPRICE Typical Price
        dataframe['typprice'] = ta.TYPPRICE(dataframe)

        #WCLPRICE Weighted Close Price
        dataframe['wclprice'] = ta.WCLPRICE(dataframe)

        '''
        //////////////////////////////////////////////////////////////////////////////////////////////////////////
        //                                                                                                      //
        //       ______              __           ____            __ _               __                         //
        //      / ____/__  __ _____ / /___       /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____     //
        //     / /    / / / // ___// // _ \      / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/     //
        //    / /___ / /_/ // /__ / //  __/    _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )      //
        //    \____/ \__, / \___//_/ \___/    /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/       //
        //          /____/                                                                                      //
        //                                                                                                      //
        //////////////////////////////////////////////////////////////////////////////////////////////////////////
        '''

        #HT_DCPERIOD Hilbert Transform - Dominant Cycle Period
        dataframe['ht_dcperiod'] = ta.HT_DCPERIOD(dataframe)

        #HT_DCPHASE Hilbert Transform - Dominant Cycle Phase
        dataframe['ht_dcphase'] = ta.HT_DCPHASE(dataframe)

        #HT_PHASOR Hilbert Transform - Phasor Components
        dataframe['ht_phasor_inphase'], dataframe['ht_phasor_quadrature'] = ta.HT_PHASOR(dataframe)

        #HT_SINE Hilbert Transform - SineWave
        dataframe['ht_sine'], dataframe['ht_leadsine'] = ta.HT_SINE(dataframe)

        #HT_TRENDMODE Hilbert Transform - Trend vs Cycle Mode
        dataframe['ht_trendmode'] = ta.HT_TRENDMODE(dataframe)














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
