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
    use_custom_stoploss = True
    can_short = False
    process_only_new_candles = True
    
    startup_candle_count = 288

    def informative_pairs(self):
        pairs = [(pair, tf) for pair in self.dp.current_whitelist() for tf in self.inf_timeframes]
        return pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        





        # '''
        # ////////////////////////////////////////////////////////////////////////////////////////////////////
        # //                                                                                                //
        # //       ____                      __                  _____  __              __ _                //
        # //      / __ \ _   __ ___   _____ / /____ _ ____      / ___/ / /_ __  __ ____/ /(_)___   _____    //
        # //     / / / /| | / // _ \ / ___// // __ `// __ \     \__ \ / __// / / // __  // // _ \ / ___/    //
        # //    / /_/ / | |/ //  __// /   / // /_/ // /_/ /    ___/ // /_ / /_/ // /_/ // //  __/(__  )     //
        # //    \____/  |___/ \___//_/   /_/ \__,_// .___/    /____/ \__/ \__,_/ \__,_//_/ \___//____/      //
        # //                                      /_/                                                       //
        # //                                                                                                //
        # ////////////////////////////////////////////////////////////////////////////////////////////////////
        # '''

        # #BBANDS Bollinger Bands
        dataframe['bb_upper'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['upperband']
        dataframe['bb_middle'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['middleband']
        dataframe['bb_lower'] = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0)['lowerband']
        dataframe['bbands_breakout_down'] = dataframe['close'] < dataframe['bb_lower']

        

        # #DEMA Double Exponential Moving Average
        # dataframe['dema_7'] = ta.DEMA(dataframe, timeperiod=7)
        # dataframe['dema_25'] = ta.DEMA(dataframe, timeperiod=25)
        # dataframe['dema_99'] = ta.DEMA(dataframe, timeperiod=99)
        # dataframe['dema_200'] = ta.DEMA(dataframe, timeperiod=200)

        # #EMA Exponential Moving Average
        dataframe['ema_7'] = ta.EMA(dataframe, timeperiod=7)
        dataframe['ema_25'] = ta.EMA(dataframe, timeperiod=25)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_99'] = ta.EMA(dataframe, timeperiod=99)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)

        # #FEMA Fibonacci Exponenetial Moving Average
        # dataframe['fema_3'] = ta.EMA(dataframe, timeperiod=3)
        # dataframe['fema_5'] = ta.EMA(dataframe, timeperiod=5)
        # dataframe['fema_8'] = ta.EMA(dataframe, timeperiod=8)
        # dataframe['fema_13'] = ta.EMA(dataframe, timeperiod=13)
        # dataframe['fema_21'] = ta.EMA(dataframe, timeperiod=21)
        # dataframe['fema_34'] = ta.EMA(dataframe, timeperiod=34)
        # dataframe['fema_55'] = ta.EMA(dataframe, timeperiod=55)
        # dataframe['fema_89'] = ta.EMA(dataframe, timeperiod=89)
        # dataframe['fema_144'] = ta.EMA(dataframe, timeperiod=144)
        # dataframe['fema_233'] = ta.EMA(dataframe, timeperiod=233)

        # #HT_TRENDLINE Hilbert Transform - Instantaneous Trendline
        # dataframe['ht_trendline'] = ta.HT_TRENDLINE(dataframe)

        # #KAMA Kaufman Adaptive Moving Average
        dataframe['kama_7'] = ta.KAMA(dataframe, timeperiod=7)
        dataframe['kama_25'] = ta.KAMA(dataframe, timeperiod=25)
        dataframe['kama_99'] = ta.KAMA(dataframe, timeperiod=99)
        dataframe['kama_200'] = ta.KAMA(dataframe, timeperiod=200)
        dataframe['kama_trend_up'] = dataframe['kama_25'] > dataframe['kama_25'].shift(1)
        dataframe['kama_trend_down'] = dataframe['kama_25'] < dataframe['kama_25'].shift(1)

        # #MA Moving average


        # #MAMA MESA Adaptive Moving Average
        # dataframe['mama'], dataframe['fama'] = ta.MAMA(dataframe)

        # #MAVP Moving average with variable period


        # #MIDPOINT MidPoint over period
        # dataframe['midpoint_7'] = ta.MIDPOINT(dataframe, timeperiod=7)
        # dataframe['midpoint_25'] = ta.MIDPOINT(dataframe, timeperiod=25)
        # dataframe['midpoint_99'] = ta.MIDPOINT(dataframe, timeperiod=99)
        # dataframe['midpoint_200'] = ta.MIDPOINT(dataframe, timeperiod=200)

        # #MIDPRICE Midpoint Price over period
        # dataframe['midprice_7'] = ta.MIDPRICE(dataframe, timeperiod=7)
        # dataframe['midprice_25'] = ta.MIDPRICE(dataframe, timeperiod=25)
        # dataframe['midprice_99'] = ta.MIDPRICE(dataframe, timeperiod=99)
        # dataframe['midprice_200'] = ta.MIDPRICE(dataframe, timeperiod=200)
        
        # #SAR Parabolic SAR
        dataframe['sar'] = ta.SAR(dataframe)

        # #SAREXT Parabolic SAR - Extended
        # dataframe['sarext'] = ta.SAREXT(dataframe)

        # #SMA Simple Moving Average
        # dataframe['sma_7'] = ta.SMA(dataframe, timeperiod=7)
        # dataframe['sma_25'] = ta.SMA(dataframe, timeperiod=25)
        # dataframe['sma_99'] = ta.SMA(dataframe, timeperiod=99)
        # dataframe['sma_200'] = ta.SMA(dataframe, timeperiod=200)

        # #T3 Triple Exponential Moving Average (T3)
        # dataframe['t3_7'] = ta.T3(dataframe, timeperiod=7)
        # dataframe['t3_25'] = ta.T3(dataframe, timeperiod=25)
        # dataframe['t3_99'] = ta.T3(dataframe, timeperiod=99)
        # dataframe['t3_200'] = ta.T3(dataframe, timeperiod=200)

        # #TEMA Triple Exponential Moving Average
        # dataframe['tema_7'] = ta.TEMA(dataframe, timeperiod=20)
        # dataframe['tema_25'] = ta.TEMA(dataframe, timeperiod=25)
        # dataframe['tema_99'] = ta.TEMA(dataframe, timeperiod=99)
        # dataframe['tema_200'] = ta.TEMA(dataframe, timeperiod=200)

        # #TRIMA Triangular Moving Average
        # dataframe['trima_7'] = ta.TRIMA(dataframe, timeperiod=7)
        # dataframe['trima_25'] = ta.TRIMA(dataframe, timeperiod=25)
        # dataframe['trima_99'] = ta.TRIMA(dataframe, timeperiod=99)
        # dataframe['trima_200'] = ta.TRIMA(dataframe, timeperiod=200)

        # #WMA Weighted Moving Average
        # dataframe['wma_7'] = ta.WMA(dataframe, timeperiod=7)
        # dataframe['wma_25'] = ta.WMA(dataframe, timeperiod=25)
        # dataframe['wma_99'] = ta.WMA(dataframe, timeperiod=99)
        # dataframe['wma_200'] = ta.WMA(dataframe, timeperiod=200)

        # '''
        # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //                                                                                                                                        //
        # //        __  ___                                __                         ____            __ _               __                         //
        # //       /  |/  /____   ____ ___   ___   ____   / /_ __  __ ____ ___       /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____     //
        # //      / /|_/ // __ \ / __ `__ \ / _ \ / __ \ / __// / / // __ `__ \      / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/     //
        # //     / /  / // /_/ // / / / / //  __// / / // /_ / /_/ // / / / / /    _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )      //
        # //    /_/  /_/ \____//_/ /_/ /_/ \___//_/ /_/ \__/ \__,_//_/ /_/ /_/    /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/       //
        # //                                                                                                                                        //
        # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # '''

        # #ADX Average Directional Movement Index
        dataframe['adx'] = ta.ADX(dataframe)

        # #ADXR Average Directional Movement Index Rating
        # dataframe['adxr'] = ta.ADXR(dataframe)

        # #APO Absolute Price Oscillator
        # dataframe['apo'] = ta.APO(dataframe)

        # #AROON Aroon
        # aroon_down, aroon_up = ta.AROON(dataframe)
        # dataframe['aroon_down'] = aroon_down
        # dataframe['aroon_up'] = aroon_up

        # #AROONOSC Aroon Oscillator
        # dataframe['aroonosc'] = ta.AROONOSC(dataframe)

        # #BOP Balance Of Power
        # dataframe['bop'] = ta.BOP(dataframe)

        # #CCI Commodity Channel Index
        dataframe['cci'] = ta.CCI(dataframe)

        # #CMO Chande Momentum Oscillator
        # dataframe['cmo'] = ta.CMO(dataframe)

        # #DX Directional Movement Index
        # dataframe['dx'] = ta.DX(dataframe)

        # #MACD Moving Average Convergence/Divergence
        macd, macdsignal, macdhist = ta.MACD(dataframe)
        dataframe['macd'] = macd
        dataframe['macdsignal'] = macdsignal
        dataframe['macdhist'] = macdhist

        # #MACDEXT MACD with controllable MA type
        # dataframe['macdext'], _, _ = ta.MACDEXT(dataframe)
        
        # #MACDFIX Moving Average Convergence/Divergence Fix 12/26
        # dataframe['macdfix'], _, _ = ta.MACDFIX(dataframe)

        # #MFI Money Flow Index
        dataframe['mfi'] = ta.MFI(dataframe)

        # #MINUS_DI Minus Directional Indicator
        dataframe['minus_di'] = ta.MINUS_DI(dataframe)

        # #MINUS_DM Minus Directional Movement
        # dataframe['minus_dm'] = ta.MINUS_DM(dataframe)

        # #MOM Momentum
        # dataframe['mom'] = ta.MOM(dataframe)

        # #PLUS_DI Plus Directional Indicator
        dataframe['plus_di'] = ta.PLUS_DI(dataframe)

        # #PLUS_DM Plus Directional Movement
        # dataframe['plus_dm'] = ta.PLUS_DM(dataframe)

        # #PPO Percentage Price Oscillator
        # dataframe['ppo'] = ta.PPO(dataframe)

        # #ROC Rate of change : ((price/prevPrice)-1)*100
        # dataframe['roc'] = ta.ROC(dataframe)

        # #ROCP Rate of change Percentage: (price-prevPrice)/prevPrice
        # dataframe['rocp'] = ta.ROCP(dataframe)

        # #ROCR Rate of change ratio: (price/prevPrice)
        # dataframe['rocr'] = ta.ROCR(dataframe)

        # #ROCR100 Rate of change ratio 100 scale: (price/prevPrice)*100
        # dataframe['rocr100'] = ta.ROCR100(dataframe)

        # #RSI Relative Strength Index
        dataframe['rsi_3'] = ta.RSI(dataframe,timeperiod=3)
        dataframe['rsi_5'] = ta.RSI(dataframe,timeperiod=5)
        dataframe['rsi_8'] = ta.RSI(dataframe,timeperiod=8)
        dataframe['rsi_13'] = ta.RSI(dataframe,timeperiod=13)
        dataframe['rsi_21'] = ta.RSI(dataframe,timeperiod=21)
        dataframe['rsi_34'] = ta.RSI(dataframe,timeperiod=34)

        # #STOCH Stochastic
        # slowk, slowd = ta.STOCH(dataframe)
        # dataframe['stoch_k'] = slowk
        # dataframe['stoch_d'] = slowd

        # #STOCHF Stochastic Fast
        # fastk, fastd = ta.STOCHF(dataframe)
        # dataframe['stochf_k'] = fastk
        # dataframe['stochf_d'] = fastd
        
        # #STOCHRSI Stochastic Relative Strength Index
        # dataframe['stochrsi_k'], dataframe['stochrsi_d'] = ta.STOCHRSI(dataframe)

        # #TRIX 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        dataframe['trix'] = ta.TRIX(dataframe)

        # #ULTOSC Ultimate Oscillator
        # dataframe['ultosc'] = ta.ULTOSC(dataframe)

        # #WILLR Williams' %R
        # dataframe['willr'] = ta.WILLR(dataframe)


        # '''
        # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //                                                                                                                //
        # //     _    __        __                             ____            __ _               __                        //
        # //    | |  / /____   / /__  __ ____ ___   ___       /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____    //
        # //    | | / // __ \ / // / / // __ `__ \ / _ \      / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/    //
        # //    | |/ // /_/ // // /_/ // / / / / //  __/    _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )     //
        # //    |___/ \____//_/ \__,_//_/ /_/ /_/ \___/    /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/      //
        # //                                                                                                                //
        # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # '''

        # #AD Chaikin A/D Line
        # dataframe['ad'] = ta.AD(dataframe)

        # #ADOSC Chaikin A/D Oscillator
        # dataframe['adosc'] = ta.ADOSC(dataframe)

        # #OBV On Balance Volume
        dataframe['obv'] = ta.OBV(dataframe)


        # '''
        # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //                                                                                                                        //
        # //     _    __        __        __   _  __ _  __             ____            __ _               __                        //
        # //    | |  / /____   / /____ _ / /_ (_)/ /(_)/ /_ __  __    /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____    //
        # //    | | / // __ \ / // __ `// __// // // // __// / / /    / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/    //
        # //    | |/ // /_/ // // /_/ // /_ / // // // /_ / /_/ /   _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )     //
        # //    |___/ \____//_/ \__,_/ \__//_//_//_/ \__/ \__, /   /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/      //
        # //                                             /____/                                                                     //
        # //                                                                                                                        //
        # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # '''

        # #ATR Average True Range
        # dataframe['atr'] = ta.ATR(dataframe)

        # #NATR Normalized Average True Range
        # dataframe['natr'] = ta.NATR(dataframe)

        # #TRANGE True Range
        # dataframe['trange'] = ta.TRANGE(dataframe)


        # '''
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //                                                                                                      //
        # //        ____         _                ______                           ____                           //
        # //       / __ \ _____ (_)_____ ___     /_  __/_____ ____ _ ____   _____ / __/____   _____ ____ ___      //
        # //      / /_/ // ___// // ___// _ \     / /  / ___// __ `// __ \ / ___// /_ / __ \ / ___// __ `__ \     //
        # //     / ____// /   / // /__ /  __/    / /  / /   / /_/ // / / /(__  )/ __// /_/ // /   / / / / / /     //
        # //    /_/    /_/   /_/ \___/ \___/    /_/  /_/    \__,_//_/ /_//____//_/   \____//_/   /_/ /_/ /_/      //
        # //                                                                                                      //
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////
        # '''

        # #AVGPRICE Average Price
        # dataframe['avgprice'] = ta.AVGPRICE(dataframe)

        # #MEDPRICE Median Price
        # dataframe['medprice'] = ta.MEDPRICE(dataframe)

        # #TYPPRICE Typical Price
        # dataframe['typprice'] = ta.TYPPRICE(dataframe)

        # #WCLPRICE Weighted Close Price
        # dataframe['wclprice'] = ta.WCLPRICE(dataframe)

        # '''
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //                                                                                                      //
        # //       ______              __           ____            __ _               __                         //
        # //      / ____/__  __ _____ / /___       /  _/____   ____/ /(_)_____ ____ _ / /_ ____   _____ _____     //
        # //     / /    / / / // ___// // _ \      / / / __ \ / __  // // ___// __ `// __// __ \ / ___// ___/     //
        # //    / /___ / /_/ // /__ / //  __/    _/ / / / / // /_/ // // /__ / /_/ // /_ / /_/ // /   (__  )      //
        # //    \____/ \__, / \___//_/ \___/    /___//_/ /_/ \__,_//_/ \___/ \__,_/ \__/ \____//_/   /____/       //
        # //          /____/                                                                                      //
        # //                                                                                                      //
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////
        # '''

        # #HT_DCPERIOD Hilbert Transform - Dominant Cycle Period
        dataframe['ht_dcperiod'] = ta.HT_DCPERIOD(dataframe)

        # #HT_DCPHASE Hilbert Transform - Dominant Cycle Phase
        # dataframe['ht_dcphase'] = ta.HT_DCPHASE(dataframe)

        # #HT_PHASOR Hilbert Transform - Phasor Components
        # dataframe['ht_phasor_inphase'], dataframe['ht_phasor_quadrature'] = ta.HT_PHASOR(dataframe)

        # #HT_SINE Hilbert Transform - SineWave
        # dataframe['ht_sine'], dataframe['ht_leadsine'] = ta.HT_SINE(dataframe)

        # #HT_TRENDMODE Hilbert Transform - Trend vs Cycle Mode
        # dataframe['ht_trendmode'] = ta.HT_TRENDMODE(dataframe)


        informative_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        informative_4h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='4h')
        informative_1d = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1d')
        informative_1w = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1w')

        # '''
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //                                                                                                                                      //
        # //         _____   ____________  ____  __  ______  ___________    ________   _____   ______  _____________  __________  ____  _____     //
        # //        /  _/ | / / ____/ __ \/ __ \/  |/  /   |/_  __/  _/ |  / / ____/  /  _/ | / / __ \/  _/ ____/   |/_  __/ __ \/ __ \/ ___/     //
        # //        / //  |/ / /_  / / / / /_/ / /|_/ / /| | / /  / / | | / / __/     / //  |/ / / / // // /   / /| | / / / / / / /_/ /\__ \      //
        # //      _/ // /|  / __/ / /_/ / _, _/ /  / / ___ |/ / _/ /  | |/ / /___   _/ // /|  / /_/ // // /___/ ___ |/ / / /_/ / _, _/___/ /      //
        # //     /___/_/ |_/_/    \____/_/ |_/_/  /_/_/  |_/_/ /___/  |___/_____/  /___/_/ |_/_____/___/\____/_/  |_/_/  \____/_/ |_|/____/       //
        # //                                                                                                                                      //
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # '''

        # #BBANDS Bollinger Bands

        informative_1h['bb_upper'] = ta.BBANDS(informative_1h, nbdevup=2.0, nbdevdn=2.0)['upperband']
        informative_1h['bb_middle'] = ta.BBANDS(informative_1h, nbdevup=2.0, nbdevdn=2.0)['middleband']
        informative_1h['bb_lower'] = ta.BBANDS(informative_1h, nbdevup=2.0, nbdevdn=2.0)['lowerband']
        informative_1h['bbands_breakout_down'] = informative_1h['close'] < informative_1h['bb_lower']

        # #DEMA Double Exponential Moving Average
        # informative_1h['dema_7'] = ta.DEMA(informative_1h, timeperiod=7)
        # informative_1h['dema_25'] = ta.DEMA(informative_1h, timeperiod=25)
        # informative_1h['dema_99'] = ta.DEMA(informative_1h, timeperiod=99)
        # informative_1h['dema_200'] = ta.DEMA(informative_1h, timeperiod=200)

        # #EMA Exponential Moving Average
        informative_1h['ema_7'] = ta.EMA(informative_1h, timeperiod=7)
        informative_1h['ema_25'] = ta.EMA(informative_1h, timeperiod=25)
        informative_1h['ema_50'] = ta.EMA(informative_1h, timeperiod=50)        
        informative_1h['ema_99'] = ta.EMA(informative_1h, timeperiod=99)
        informative_1h['ema_200'] = ta.EMA(informative_1h, timeperiod=200)

        # #FEMA Fibonacci Exponenetial Moving Average
        # informative_1h['fema_3'] = ta.EMA(informative_1h, timeperiod=3)
        # informative_1h['fema_5'] = ta.EMA(informative_1h, timeperiod=5)
        # informative_1h['fema_8'] = ta.EMA(informative_1h, timeperiod=8)
        # informative_1h['fema_13'] = ta.EMA(informative_1h, timeperiod=13)
        # informative_1h['fema_21'] = ta.EMA(informative_1h, timeperiod=21)
        # informative_1h['fema_34'] = ta.EMA(informative_1h, timeperiod=34)
        # informative_1h['fema_55'] = ta.EMA(informative_1h, timeperiod=55)
        # informative_1h['fema_89'] = ta.EMA(informative_1h, timeperiod=89)
        # informative_1h['fema_144'] = ta.EMA(informative_1h, timeperiod=144)
        # informative_1h['fema_233'] = ta.EMA(informative_1h, timeperiod=233)

        # #HT_TRENDLINE Hilbert Transform - Instantaneous Trendline
        # informative_1h['ht_trendline'] = ta.HT_TRENDLINE(informative_1h)

        # #KAMA Kaufman Adaptive Moving Average
        informative_1h['kama_7'] = ta.KAMA(informative_1h, timeperiod=7)
        informative_1h['kama_25'] = ta.KAMA(informative_1h, timeperiod=25)
        informative_1h['kama_99'] = ta.KAMA(informative_1h, timeperiod=99)
        informative_1h['kama_200'] = ta.KAMA(informative_1h, timeperiod=200)
        informative_1h['kama_trend_up'] = informative_1h['kama_99'] > informative_1h['kama_99'].shift(1)
        informative_1h['kama_trend_down'] = informative_1h['kama_99'] < informative_1h['kama_99'].shift(1)

        # #MA Moving average


        # #MAMA MESA Adaptive Moving Average
        # informative_1h['mama'], informative_1h['fama'] = ta.MAMA(informative_1h)

        # #MAVP Moving average with variable period


        # #MIDPOINT MidPoint over period
        # informative_1h['midpoint_7'] = ta.MIDPOINT(informative_1h, timeperiod=7)
        # informative_1h['midpoint_25'] = ta.MIDPOINT(informative_1h, timeperiod=25)
        # informative_1h['midpoint_99'] = ta.MIDPOINT(informative_1h, timeperiod=99)
        # informative_1h['midpoint_200'] = ta.MIDPOINT(informative_1h, timeperiod=200)

        # #MIDPRICE Midpoint Price over period
        # informative_1h['midprice_7'] = ta.MIDPRICE(informative_1h, timeperiod=7)
        # informative_1h['midprice_25'] = ta.MIDPRICE(informative_1h, timeperiod=25)
        # informative_1h['midprice_99'] = ta.MIDPRICE(informative_1h, timeperiod=99)
        # informative_1h['midprice_200'] = ta.MIDPRICE(informative_1h, timeperiod=200)
        
        # #SAR Parabolic SAR
        informative_1h['sar'] = ta.SAR(informative_1h)

        # #SAREXT Parabolic SAR - Extended
        # informative_1h['sarext'] = ta.SAREXT(informative_1h)

        # #SMA Simple Moving Average
        # informative_1h['sma_7'] = ta.SMA(informative_1h, timeperiod=7)
        # informative_1h['sma_25'] = ta.SMA(informative_1h, timeperiod=25)
        # informative_1h['sma_99'] = ta.SMA(informative_1h, timeperiod=99)
        # informative_1h['sma_200'] = ta.SMA(informative_1h, timeperiod=200)

        # #T3 Triple Exponential Moving Average (T3)
        # informative_1h['t3_7'] = ta.T3(informative_1h, timeperiod=7)
        # informative_1h['t3_25'] = ta.T3(informative_1h, timeperiod=25)
        # informative_1h['t3_99'] = ta.T3(informative_1h, timeperiod=99)
        # informative_1h['t3_200'] = ta.T3(informative_1h, timeperiod=200)

        # #TEMA Triple Exponential Moving Average
        # informative_1h['tema_7'] = ta.TEMA(informative_1h, timeperiod=20)
        # informative_1h['tema_25'] = ta.TEMA(informative_1h, timeperiod=25)
        # informative_1h['tema_99'] = ta.TEMA(informative_1h, timeperiod=99)
        # informative_1h['tema_200'] = ta.TEMA(informative_1h, timeperiod=200)

        # #TRIMA Triangular Moving Average
        # informative_1h['trima_7'] = ta.TRIMA(informative_1h, timeperiod=7)
        # informative_1h['trima_25'] = ta.TRIMA(informative_1h, timeperiod=25)
        # informative_1h['trima_99'] = ta.TRIMA(informative_1h, timeperiod=99)
        # informative_1h['trima_200'] = ta.TRIMA(informative_1h, timeperiod=200)

        # #WMA Weighted Moving Average
        # informative_1h['wma_7'] = ta.WMA(informative_1h, timeperiod=7)
        # informative_1h['wma_25'] = ta.WMA(informative_1h, timeperiod=25)
        # informative_1h['wma_99'] = ta.WMA(informative_1h, timeperiod=99)
        # informative_1h['wma_200'] = ta.WMA(informative_1h, timeperiod=200)

        # #ADX Average Directional Movement Index
        informative_1h['adx'] = ta.ADX(informative_1h)

        # #ADXR Average Directional Movement Index Rating
        # informative_1h['adxr'] = ta.ADXR(informative_1h)

        # #APO Absolute Price Oscillator
        # informative_1h['apo'] = ta.APO(informative_1h)

        # #AROON Aroon

        # #AROONOSC Aroon Oscillator
        # informative_1h['aroonosc'] = ta.AROONOSC(informative_1h)

        # #BOP Balance Of Power
        # informative_1h['bop'] = ta.BOP(informative_1h)

        # #CCI Commodity Channel Index
        informative_1h['cci'] = ta.CCI(informative_1h)

        # #CMO Chande Momentum Oscillator
        # informative_1h['cmo'] = ta.CMO(informative_1h)

        # #DX Directional Movement Index
        # informative_1h['dx'] = ta.DX(informative_1h)

        # #MACD Moving Average Convergence/Divergence
        macd, macdsignal, macdhist = ta.MACD(informative_1h)
        informative_1h['macd'] = macd
        informative_1h['macdsignal'] = macdsignal
        informative_1h['macdhist'] = macdhist

        # #MACDEXT MACD with controllable MA type
        # informative_1h['macdext'], _, _ = ta.MACDEXT(informative_1h)
        
        # #MACDFIX Moving Average Convergence/Divergence Fix 12/26
        # informative_1h['macdfix'], _, _ = ta.MACDFIX(informative_1h)

        # #MFI Money Flow Index
        informative_1h['mfi'] = ta.MFI(informative_1h)

        # #MINUS_DI Minus Directional Indicator
        informative_1h['minus_di'] = ta.MINUS_DI(informative_1h)

        # #MINUS_DM Minus Directional Movement
        # informative_1h['minus_dm'] = ta.MINUS_DM(informative_1h)

        # #MOM Momentum
        # informative_1h['mom'] = ta.MOM(informative_1h)

        # #PLUS_DI Plus Directional Indicator
        informative_1h['plus_di'] = ta.PLUS_DI(informative_1h)

        # #PLUS_DM Plus Directional Movement
        # informative_1h['plus_dm'] = ta.PLUS_DM(informative_1h)

        # #PPO Percentage Price Oscillator
        # informative_1h['ppo'] = ta.PPO(informative_1h)

        # #ROC Rate of change : ((price/prevPrice)-1)*100
        informative_1h['roc'] = ta.ROC(informative_1h)

        # #ROCP Rate of change Percentage: (price-prevPrice)/prevPrice
        # informative_1h['rocp'] = ta.ROCP(informative_1h)

        # #ROCR Rate of change ratio: (price/prevPrice)
        # informative_1h['rocr'] = ta.ROCR(informative_1h)

        # #ROCR100 Rate of change ratio 100 scale: (price/prevPrice)*100
        # informative_1h['rocr100'] = ta.ROCR100(informative_1h)

        # #RSI Relative Strength Index
        informative_1h['rsi_3'] = ta.RSI(informative_1h,timeperiod=3)
        informative_1h['rsi_5'] = ta.RSI(informative_1h,timeperiod=5)
        informative_1h['rsi_8'] = ta.RSI(informative_1h,timeperiod=8)
        informative_1h['rsi_13'] = ta.RSI(informative_1h,timeperiod=13)
        informative_1h['rsi_21'] = ta.RSI(informative_1h,timeperiod=21)
        informative_1h['rsi_34'] = ta.RSI(informative_1h,timeperiod=34)

        # #STOCH Stochastic
        # slowk, slowd = ta.STOCH(informative_1h)
        # informative_1h['stoch_k'] = slowk
        # informative_1h['stoch_d'] = slowd

        # #STOCHF Stochastic Fast
        # fastk, fastd = ta.STOCHF(informative_1h)
        # informative_1h['stochf_k'] = fastk
        # informative_1h['stochf_d'] = fastd
        
        # #STOCHRSI Stochastic Relative Strength Index
        # informative_1h['stochrsi_k'], informative_1h['stochrsi_d'] = ta.STOCHRSI(informative_1h)

        # #TRIX 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        informative_1h['trix'] = ta.TRIX(informative_1h)

        # #ULTOSC Ultimate Oscillator
        # informative_1h['ultosc'] = ta.ULTOSC(informative_1h)

        # #WILLR Williams' %R
        # informative_1h['willr'] = ta.WILLR(informative_1h)

        # #BBANDS Bollinger Bands
        informative_4h['bb_upper'] = ta.BBANDS(informative_4h, nbdevup=2.0, nbdevdn=2.0)['upperband']
        informative_4h['bb_middle'] = ta.BBANDS(informative_4h, nbdevup=2.0, nbdevdn=2.0)['middleband']
        informative_4h['bb_lower'] = ta.BBANDS(informative_4h, nbdevup=2.0, nbdevdn=2.0)['lowerband']
        informative_4h['bbands_breakout_down'] = informative_4h['close'] < informative_4h['bb_lower']

        # #DEMA Double Exponential Moving Average
        # informative_4h['dema_7'] = ta.DEMA(informative_4h, timeperiod=7)
        # informative_4h['dema_25'] = ta.DEMA(informative_4h, timeperiod=25)
        # informative_4h['dema_99'] = ta.DEMA(informative_4h, timeperiod=99)
        # informative_4h['dema_200'] = ta.DEMA(informative_4h, timeperiod=200)

        # #EMA Exponential Moving Average
        informative_4h['ema_7'] = ta.EMA(informative_4h, timeperiod=7)
        informative_4h['ema_25'] = ta.EMA(informative_4h, timeperiod=25)
        informative_4h['ema_50'] = ta.EMA(informative_4h, timeperiod=50)
        informative_4h['ema_99'] = ta.EMA(informative_4h, timeperiod=99)
        informative_4h['ema_200'] = ta.EMA(informative_4h, timeperiod=200)

        # #FEMA Fibonacci Exponenetial Moving Average
        # informative_4h['fema_3'] = ta.EMA(informative_4h, timeperiod=3)
        # informative_4h['fema_5'] = ta.EMA(informative_4h, timeperiod=5)
        # informative_4h['fema_8'] = ta.EMA(informative_4h, timeperiod=8)
        # informative_4h['fema_13'] = ta.EMA(informative_4h, timeperiod=13)
        # informative_4h['fema_21'] = ta.EMA(informative_4h, timeperiod=21)
        # informative_4h['fema_34'] = ta.EMA(informative_4h, timeperiod=34)
        # informative_4h['fema_55'] = ta.EMA(informative_4h, timeperiod=55)
        # informative_4h['fema_89'] = ta.EMA(informative_4h, timeperiod=89)
        # informative_4h['fema_144'] = ta.EMA(informative_4h, timeperiod=144)
        # informative_4h['fema_233'] = ta.EMA(informative_4h, timeperiod=233)

        # #HT_TRENDLINE Hilbert Transform - Instantaneous Trendline
        # informative_4h['ht_trendline'] = ta.HT_TRENDLINE(informative_4h)

        # #KAMA Kaufman Adaptive Moving Average
        informative_4h['kama_7'] = ta.KAMA(informative_4h, timeperiod=7)
        informative_4h['kama_25'] = ta.KAMA(informative_4h, timeperiod=25)
        informative_4h['kama_99'] = ta.KAMA(informative_4h, timeperiod=99)
        informative_4h['kama_200'] = ta.KAMA(informative_4h, timeperiod=200)
        informative_4h['kama_trend_up'] = informative_4h['kama_99'] > informative_4h['kama_99'].shift(1)
        informative_4h['kama_trend_down'] = informative_4h['kama_99'] < informative_4h['kama_99'].shift(1)

        # #MA Moving average


        # #MAMA MESA Adaptive Moving Average
        # informative_4h['mama'], informative_4h['fama'] = ta.MAMA(informative_4h)

        # #MAVP Moving average with variable period


        # #MIDPOINT MidPoint over period
        # informative_4h['midpoint_7'] = ta.MIDPOINT(informative_4h, timeperiod=7)
        # informative_4h['midpoint_25'] = ta.MIDPOINT(informative_4h, timeperiod=25)
        # informative_4h['midpoint_99'] = ta.MIDPOINT(informative_4h, timeperiod=99)
        # informative_4h['midpoint_200'] = ta.MIDPOINT(informative_4h, timeperiod=200)

        # #MIDPRICE Midpoint Price over period
        # informative_4h['midprice_7'] = ta.MIDPRICE(informative_4h, timeperiod=7)
        # informative_4h['midprice_25'] = ta.MIDPRICE(informative_4h, timeperiod=25)
        # informative_4h['midprice_99'] = ta.MIDPRICE(informative_4h, timeperiod=99)
        # informative_4h['midprice_200'] = ta.MIDPRICE(informative_4h, timeperiod=200)
        
        # #SAR Parabolic SAR
        informative_4h['sar'] = ta.SAR(informative_4h)

        # #SAREXT Parabolic SAR - Extended
        # informative_4h['sarext'] = ta.SAREXT(informative_4h)

        # #SMA Simple Moving Average
        # informative_4h['sma_7'] = ta.SMA(informative_4h, timeperiod=7)
        # informative_4h['sma_25'] = ta.SMA(informative_4h, timeperiod=25)
        # informative_4h['sma_99'] = ta.SMA(informative_4h, timeperiod=99)
        # informative_4h['sma_200'] = ta.SMA(informative_4h, timeperiod=200)

        # #T3 Triple Exponential Moving Average (T3)
        # informative_4h['t3_7'] = ta.T3(informative_4h, timeperiod=7)
        # informative_4h['t3_25'] = ta.T3(informative_4h, timeperiod=25)
        # informative_4h['t3_99'] = ta.T3(informative_4h, timeperiod=99)
        # informative_4h['t3_200'] = ta.T3(informative_4h, timeperiod=200)

        # #TEMA Triple Exponential Moving Average
        # informative_4h['tema_7'] = ta.TEMA(informative_4h, timeperiod=20)
        # informative_4h['tema_25'] = ta.TEMA(informative_4h, timeperiod=25)
        # informative_4h['tema_99'] = ta.TEMA(informative_4h, timeperiod=99)
        # informative_4h['tema_200'] = ta.TEMA(informative_4h, timeperiod=200)

        # #TRIMA Triangular Moving Average
        # informative_4h['trima_7'] = ta.TRIMA(informative_4h, timeperiod=7)
        # informative_4h['trima_25'] = ta.TRIMA(informative_4h, timeperiod=25)
        # informative_4h['trima_99'] = ta.TRIMA(informative_4h, timeperiod=99)
        # informative_4h['trima_200'] = ta.TRIMA(informative_4h, timeperiod=200)

        # #WMA Weighted Moving Average
        # informative_4h['wma_7'] = ta.WMA(informative_4h, timeperiod=7)
        # informative_4h['wma_25'] = ta.WMA(informative_4h, timeperiod=25)
        # informative_4h['wma_99'] = ta.WMA(informative_4h, timeperiod=99)
        # informative_4h['wma_200'] = ta.WMA(informative_4h, timeperiod=200)

        # #ADX Average Directional Movement Index
        informative_4h['adx'] = ta.ADX(informative_4h)

        # #ADXR Average Directional Movement Index Rating
        # informative_4h['adxr'] = ta.ADXR(informative_4h)

        # #APO Absolute Price Oscillator
        # informative_4h['apo'] = ta.APO(informative_4h)

        # #AROON Aroon

        # #AROONOSC Aroon Oscillator
        # informative_4h['aroonosc'] = ta.AROONOSC(informative_4h)

        # #BOP Balance Of Power
        # informative_4h['bop'] = ta.BOP(informative_4h)

        # #CCI Commodity Channel Index
        informative_4h['cci'] = ta.CCI(informative_4h)

        # #CMO Chande Momentum Oscillator
        # informative_4h['cmo'] = ta.CMO(informative_4h)

        # #DX Directional Movement Index
        # informative_4h['dx'] = ta.DX(informative_4h)

        # #MACD Moving Average Convergence/Divergence
        macd, macdsignal, macdhist = ta.MACD(informative_4h)
        informative_4h['macd'] = macd
        informative_4h['macdsignal'] = macdsignal
        informative_4h['macdhist'] = macdhist

        # #MACDEXT MACD with controllable MA type
        # informative_4h['macdext'], _, _ = ta.MACDEXT(informative_4h)
        
        # #MACDFIX Moving Average Convergence/Divergence Fix 12/26
        # informative_4h['macdfix'], _, _ = ta.MACDFIX(informative_4h)

        # #MFI Money Flow Index
        informative_4h['mfi'] = ta.MFI(informative_4h)

        # #MINUS_DI Minus Directional Indicator
        informative_4h['minus_di'] = ta.MINUS_DI(informative_4h)

        # #MINUS_DM Minus Directional Movement
        # informative_4h['minus_dm'] = ta.MINUS_DM(informative_4h)

        # #MOM Momentum
        # informative_4h['mom'] = ta.MOM(informative_4h)

        # #PLUS_DI Plus Directional Indicator
        informative_4h['plus_di'] = ta.PLUS_DI(informative_4h)

        # #PLUS_DM Plus Directional Movement
        # informative_4h['plus_dm'] = ta.PLUS_DM(informative_4h)

        # #PPO Percentage Price Oscillator
        # informative_4h['ppo'] = ta.PPO(informative_4h)

        # #ROC Rate of change : ((price/prevPrice)-1)*100
        informative_4h['roc'] = ta.ROC(informative_4h)

        # #ROCP Rate of change Percentage: (price-prevPrice)/prevPrice
        # informative_4h['rocp'] = ta.ROCP(informative_4h)

        # #ROCR Rate of change ratio: (price/prevPrice)
        # informative_4h['rocr'] = ta.ROCR(informative_4h)

        # #ROCR100 Rate of change ratio 100 scale: (price/prevPrice)*100
        # informative_4h['rocr100'] = ta.ROCR100(informative_4h)

        # #RSI Relative Strength Index
        informative_4h['rsi_3'] = ta.RSI(informative_4h,timeperiod=3)
        informative_4h['rsi_5'] = ta.RSI(informative_4h,timeperiod=5)
        informative_4h['rsi_8'] = ta.RSI(informative_4h,timeperiod=8)
        informative_4h['rsi_13'] = ta.RSI(informative_4h,timeperiod=13)
        informative_4h['rsi_21'] = ta.RSI(informative_4h,timeperiod=21)
        informative_4h['rsi_34'] = ta.RSI(informative_4h,timeperiod=34)

        # #STOCH Stochastic
        # slowk, slowd = ta.STOCH(informative_4h)
        # informative_4h['stoch_k'] = slowk
        # informative_4h['stoch_d'] = slowd

        # #STOCHF Stochastic Fast
        # fastk, fastd = ta.STOCHF(informative_4h)
        # informative_4h['stochf_k'] = fastk
        # informative_4h['stochf_d'] = fastd
        
        # #STOCHRSI Stochastic Relative Strength Index
        # informative_4h['stochrsi_k'], informative_4h['stochrsi_d'] = ta.STOCHRSI(informative_4h)

        # #TRIX 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        informative_4h['trix'] = ta.TRIX(informative_4h)

        # #ULTOSC Ultimate Oscillator
        # informative_4h['ultosc'] = ta.ULTOSC(informative_4h)

        # #WILLR Williams' %R
        # informative_4h['willr'] = ta.WILLR(informative_4h)

        # #AD Chaikin A/D Line
        # informative_4h['ad'] = ta.AD(informative_4h)

        # #ADOSC Chaikin A/D Oscillator
        # informative_4h['adosc'] = ta.ADOSC(informative_4h)

        # #OBV On Balance Volume
        informative_4h['obv'] = ta.OBV(informative_4h)

        # #ATR Average True Range
        # informative_4h['atr'] = ta.ATR(informative_4h)

        # #NATR Normalized Average True Range
        # informative_4h['natr'] = ta.NATR(informative_4h)

        # #TRANGE True Range
        # informative_4h['trange'] = ta.TRANGE(informative_4h)

        # #AVGPRICE Average Price
        # informative_4h['avgprice'] = ta.AVGPRICE(informative_4h)

        # #MEDPRICE Median Price
        # informative_4h['medprice'] = ta.MEDPRICE(informative_4h)

        # #TYPPRICE Typical Price
        # informative_4h['typprice'] = ta.TYPPRICE(informative_4h)

        # #WCLPRICE Weighted Close Price
        # informative_4h['wclprice'] = ta.WCLPRICE(informative_4h)

        # #HT_DCPERIOD Hilbert Transform - Dominant Cycle Period
        informative_4h['ht_dcperiod'] = ta.HT_DCPERIOD(informative_4h)

        # #HT_DCPHASE Hilbert Transform - Dominant Cycle Phase
        # informative_4h['ht_dcphase'] = ta.HT_DCPHASE(informative_4h)

        # #HT_PHASOR Hilbert Transform - Phasor Components
        # informative_4h['ht_phasor_inphase'], informative_4h['ht_phasor_quadrature'] = ta.HT_PHASOR(informative_4h)

        # #HT_SINE Hilbert Transform - SineWave
        # informative_4h['ht_sine'], informative_4h['ht_leadsine'] = ta.HT_SINE(informative_4h)

        # #HT_TRENDMODE Hilbert Transform - Trend vs Cycle Mode
        # informative_4h['ht_trendmode'] = ta.HT_TRENDMODE(informative_4h)

        # #BBANDS Bollinger Bands
        informative_1d['bb_upper'] = ta.BBANDS(informative_1d, nbdevup=2.0, nbdevdn=2.0)['upperband']
        informative_1d['bb_middle'] = ta.BBANDS(informative_1d, nbdevup=2.0, nbdevdn=2.0)['middleband']
        informative_1d['bb_lower'] = ta.BBANDS(informative_1d, nbdevup=2.0, nbdevdn=2.0)['lowerband']
        informative_1d['bbands_breakout_down'] = informative_1d['close'] < informative_1d['bb_lower']

        # #DEMA Double Exponential Moving Average
        # informative_1d['dema_7'] = ta.DEMA(informative_1d, timeperiod=7)
        # informative_1d['dema_25'] = ta.DEMA(informative_1d, timeperiod=25)
        # informative_1d['dema_99'] = ta.DEMA(informative_1d, timeperiod=99)
        # informative_1d['dema_200'] = ta.DEMA(informative_1d, timeperiod=200)

        # #EMA Exponential Moving Average
        informative_1d['ema_7'] = ta.EMA(informative_1d, timeperiod=7)
        informative_1d['ema_25'] = ta.EMA(informative_1d, timeperiod=25)
        informative_1d['ema_50'] = ta.EMA(informative_1d, timeperiod=50)
        informative_1d['ema_99'] = ta.EMA(informative_1d, timeperiod=99)
        informative_1d['ema_200'] = ta.EMA(informative_1d, timeperiod=200)

        # #FEMA Fibonacci Exponenetial Moving Average
        # informative_1d['fema_3'] = ta.EMA(informative_1d, timeperiod=3)
        # informative_1d['fema_5'] = ta.EMA(informative_1d, timeperiod=5)
        # informative_1d['fema_8'] = ta.EMA(informative_1d, timeperiod=8)
        # informative_1d['fema_13'] = ta.EMA(informative_1d, timeperiod=13)
        # informative_1d['fema_21'] = ta.EMA(informative_1d, timeperiod=21)
        # informative_1d['fema_34'] = ta.EMA(informative_1d, timeperiod=34)
        # informative_1d['fema_55'] = ta.EMA(informative_1d, timeperiod=55)
        # informative_1d['fema_89'] = ta.EMA(informative_1d, timeperiod=89)
        # informative_1d['fema_144'] = ta.EMA(informative_1d, timeperiod=144)
        # informative_1d['fema_233'] = ta.EMA(informative_1d, timeperiod=233)

        # #HT_TRENDLINE Hilbert Transform - Instantaneous Trendline
        # informative_1d['ht_trendline'] = ta.HT_TRENDLINE(informative_1d)

        # #KAMA Kaufman Adaptive Moving Average
        informative_1d['kama_7'] = ta.KAMA(informative_1d, timeperiod=7)
        informative_1d['kama_25'] = ta.KAMA(informative_1d, timeperiod=25)
        informative_1d['kama_99'] = ta.KAMA(informative_1d, timeperiod=99)
        informative_1d['kama_200'] = ta.KAMA(informative_1d, timeperiod=200)
        informative_1d['kama_trend_up'] = informative_1d['kama_200'] > informative_1d['kama_200'].shift(1)
        informative_1d['kama_trend_down'] = informative_1d['kama_200'] < informative_1d['kama_200'].shift(1)

        # #MA Moving average


        # #MAMA MESA Adaptive Moving Average
        # informative_1d['mama'], informative_1d['fama'] = ta.MAMA(informative_1d)

        # #MAVP Moving average with variable period


        # #MIDPOINT MidPoint over period
        # informative_1d['midpoint_7'] = ta.MIDPOINT(informative_1d, timeperiod=7)
        # informative_1d['midpoint_25'] = ta.MIDPOINT(informative_1d, timeperiod=25)
        # informative_1d['midpoint_99'] = ta.MIDPOINT(informative_1d, timeperiod=99)
        # informative_1d['midpoint_200'] = ta.MIDPOINT(informative_1d, timeperiod=200)

        # #MIDPRICE Midpoint Price over period
        # informative_1d['midprice_7'] = ta.MIDPRICE(informative_1d, timeperiod=7)
        # informative_1d['midprice_25'] = ta.MIDPRICE(informative_1d, timeperiod=25)
        # informative_1d['midprice_99'] = ta.MIDPRICE(informative_1d, timeperiod=99)
        # informative_1d['midprice_200'] = ta.MIDPRICE(informative_1d, timeperiod=200)
        
        # #SAR Parabolic SAR
        informative_1d['sar'] = ta.SAR(informative_1d)

        # #SAREXT Parabolic SAR - Extended
        # informative_1d['sarext'] = ta.SAREXT(informative_1d)

        # #SMA Simple Moving Average
        # informative_1d['sma_7'] = ta.SMA(informative_1d, timeperiod=7)
        # informative_1d['sma_25'] = ta.SMA(informative_1d, timeperiod=25)
        # informative_1d['sma_99'] = ta.SMA(informative_1d, timeperiod=99)
        # informative_1d['sma_200'] = ta.SMA(informative_1d, timeperiod=200)

        # #T3 Triple Exponential Moving Average (T3)
        # informative_1d['t3_7'] = ta.T3(informative_1d, timeperiod=7)
        # informative_1d['t3_25'] = ta.T3(informative_1d, timeperiod=25)
        # informative_1d['t3_99'] = ta.T3(informative_1d, timeperiod=99)
        # informative_1d['t3_200'] = ta.T3(informative_1d, timeperiod=200)

        # #TEMA Triple Exponential Moving Average
        # informative_1d['tema_7'] = ta.TEMA(informative_1d, timeperiod=20)
        # informative_1d['tema_25'] = ta.TEMA(informative_1d, timeperiod=25)
        # informative_1d['tema_99'] = ta.TEMA(informative_1d, timeperiod=99)
        # informative_1d['tema_200'] = ta.TEMA(informative_1d, timeperiod=200)

        # #TRIMA Triangular Moving Average
        # informative_1d['trima_7'] = ta.TRIMA(informative_1d, timeperiod=7)
        # informative_1d['trima_25'] = ta.TRIMA(informative_1d, timeperiod=25)
        # informative_1d['trima_99'] = ta.TRIMA(informative_1d, timeperiod=99)
        # informative_1d['trima_200'] = ta.TRIMA(informative_1d, timeperiod=200)

        # #WMA Weighted Moving Average
        # informative_1d['wma_7'] = ta.WMA(informative_1d, timeperiod=7)
        # informative_1d['wma_25'] = ta.WMA(informative_1d, timeperiod=25)
        # informative_1d['wma_99'] = ta.WMA(informative_1d, timeperiod=99)
        # informative_1d['wma_200'] = ta.WMA(informative_1d, timeperiod=200)

        # #ADX Average Directional Movement Index
        informative_1d['adx'] = ta.ADX(informative_1d)

        # #ADXR Average Directional Movement Index Rating
        # informative_1d['adxr'] = ta.ADXR(informative_1d)

        # #APO Absolute Price Oscillator
        # informative_1d['apo'] = ta.APO(informative_1d)

        # #AROON Aroon

        # #AROONOSC Aroon Oscillator
        # informative_1d['aroonosc'] = ta.AROONOSC(informative_1d)

        # #BOP Balance Of Power
        # informative_1d['bop'] = ta.BOP(informative_1d)

        # #CCI Commodity Channel Index
        informative_1d['cci'] = ta.CCI(informative_1d)

        # #CMO Chande Momentum Oscillator
        # informative_1d['cmo'] = ta.CMO(informative_1d)

        # #DX Directional Movement Index
        # informative_1d['dx'] = ta.DX(informative_1d)

        # #MACD Moving Average Convergence/Divergence
        macd, macdsignal, macdhist = ta.MACD(informative_1d)
        informative_1d['macd'] = macd
        informative_1d['macdsignal'] = macdsignal
        informative_1d['macdhist'] = macdhist

        # #MACDEXT MACD with controllable MA type
        # informative_1d['macdext'], _, _ = ta.MACDEXT(informative_1d)
        
        # #MACDFIX Moving Average Convergence/Divergence Fix 12/26
        # informative_1d['macdfix'], _, _ = ta.MACDFIX(informative_1d)

        # #MFI Money Flow Index
        informative_1d['mfi'] = ta.MFI(informative_1d)

        # #MINUS_DI Minus Directional Indicator
        informative_1d['minus_di'] = ta.MINUS_DI(informative_1d)

        # #MINUS_DM Minus Directional Movement
        # informative_1d['minus_dm'] = ta.MINUS_DM(informative_1d)

        # #MOM Momentum
        # informative_1d['mom'] = ta.MOM(informative_1d)

        # #PLUS_DI Plus Directional Indicator
        informative_1d['plus_di'] = ta.PLUS_DI(informative_1d)

        # #PLUS_DM Plus Directional Movement
        # informative_1d['plus_dm'] = ta.PLUS_DM(informative_1d)

        # #PPO Percentage Price Oscillator
        # informative_1d['ppo'] = ta.PPO(informative_1d)

        # #ROC Rate of change : ((price/prevPrice)-1)*100
        informative_1d['roc'] = ta.ROC(informative_1d)

        # #ROCP Rate of change Percentage: (price-prevPrice)/prevPrice
        # informative_1d['rocp'] = ta.ROCP(informative_1d)

        # #ROCR Rate of change ratio: (price/prevPrice)
        # informative_1d['rocr'] = ta.ROCR(informative_1d)

        # #ROCR100 Rate of change ratio 100 scale: (price/prevPrice)*100
        # informative_1d['rocr100'] = ta.ROCR100(informative_1d)

        # #RSI Relative Strength Index
        informative_1d['rsi_3'] = ta.RSI(informative_1d,timeperiod=3)
        informative_1d['rsi_5'] = ta.RSI(informative_1d,timeperiod=5)
        informative_1d['rsi_8'] = ta.RSI(informative_1d,timeperiod=8)
        informative_1d['rsi_13'] = ta.RSI(informative_1d,timeperiod=13)
        informative_1d['rsi_21'] = ta.RSI(informative_1d,timeperiod=21)
        informative_1d['rsi_34'] = ta.RSI(informative_1d,timeperiod=34)

        # #STOCH Stochastic
        # slowk, slowd = ta.STOCH(informative_1d)
        # informative_1d['stoch_k'] = slowk
        # informative_1d['stoch_d'] = slowd

        # #STOCHF Stochastic Fast
        # fastk, fastd = ta.STOCHF(informative_1d)
        # informative_1d['stochf_k'] = fastk
        # informative_1d['stochf_d'] = fastd
        
        # #STOCHRSI Stochastic Relative Strength Index
        # informative_1d['stochrsi_k'], informative_1d['stochrsi_d'] = ta.STOCHRSI(informative_1d)

        # #TRIX 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        informative_1d['trix'] = ta.TRIX(informative_1d)

        # #ULTOSC Ultimate Oscillator
        # informative_1d['ultosc'] = ta.ULTOSC(informative_1d)

        # #WILLR Williams' %R
        # informative_1d['willr'] = ta.WILLR(informative_1d)

        # #AD Chaikin A/D Line
        # informative_1d['ad'] = ta.AD(informative_1d)

        # #ADOSC Chaikin A/D Oscillator
        # informative_1d['adosc'] = ta.ADOSC(informative_1d)

        # #OBV On Balance Volume
        informative_1d['obv'] = ta.OBV(informative_1d)

        # #ATR Average True Range
        # informative_1d['atr'] = ta.ATR(informative_1d)

        # #NATR Normalized Average True Range
        # informative_1d['natr'] = ta.NATR(informative_1d)

        # #TRANGE True Range
        # informative_1d['trange'] = ta.TRANGE(informative_1d)

        # #AVGPRICE Average Price
        # informative_1d['avgprice'] = ta.AVGPRICE(informative_1d)

        # #MEDPRICE Median Price
        # informative_1d['medprice'] = ta.MEDPRICE(informative_1d)

        # #TYPPRICE Typical Price
        # informative_1d['typprice'] = ta.TYPPRICE(informative_1d)

        # #WCLPRICE Weighted Close Price
        # informative_1d['wclprice'] = ta.WCLPRICE(informative_1d)

        # #HT_DCPERIOD Hilbert Transform - Dominant Cycle Period
        informative_1d['ht_dcperiod'] = ta.HT_DCPERIOD(informative_1d)

        # #HT_DCPHASE Hilbert Transform - Dominant Cycle Phase
        # informative_1d['ht_dcphase'] = ta.HT_DCPHASE(informative_1d)

        # #HT_PHASOR Hilbert Transform - Phasor Components
        # informative_1d['ht_phasor_inphase'], informative_1d['ht_phasor_quadrature'] = ta.HT_PHASOR(informative_1d)

        # #HT_SINE Hilbert Transform - SineWave
        # informative_1d['ht_sine'], informative_1d['ht_leadsine'] = ta.HT_SINE(informative_1d)

        # #HT_TRENDMODE Hilbert Transform - Trend vs Cycle Mode
        # informative_1d['ht_trendmode'] = ta.HT_TRENDMODE(informative_1d)

        # #BBANDS Bollinger Bands
        informative_1w['bb_upper'] = ta.BBANDS(informative_1w, nbdevup=2.0, nbdevdn=2.0)['upperband']
        informative_1w['bb_middle'] = ta.BBANDS(informative_1w, nbdevup=2.0, nbdevdn=2.0)['middleband']
        informative_1w['bb_lower'] = ta.BBANDS(informative_1w, nbdevup=2.0, nbdevdn=2.0)['lowerband']
        informative_1w['bbands_breakout_down'] = informative_1w['close'] < informative_1w['bb_lower']

        # #DEMA Double Exponential Moving Average
        # informative_1w['dema_7'] = ta.DEMA(informative_1w, timeperiod=7)
        # informative_1w['dema_25'] = ta.DEMA(informative_1w, timeperiod=25)
        # informative_1w['dema_99'] = ta.DEMA(informative_1w, timeperiod=99)
        # informative_1w['dema_200'] = ta.DEMA(informative_1w, timeperiod=200)

        # #EMA Exponential Moving Average
        informative_1w['ema_7'] = ta.EMA(informative_1w, timeperiod=7)
        informative_1w['ema_25'] = ta.EMA(informative_1w, timeperiod=25)
        informative_1w['ema_50'] = ta.EMA(informative_1w, timeperiod=50)
        informative_1w['ema_99'] = ta.EMA(informative_1w, timeperiod=99)
        informative_1w['ema_200'] = ta.EMA(informative_1w, timeperiod=200)

        # #FEMA Fibonacci Exponenetial Moving Average
        # informative_1w['fema_3'] = ta.EMA(informative_1w, timeperiod=3)
        # informative_1w['fema_5'] = ta.EMA(informative_1w, timeperiod=5)
        # informative_1w['fema_8'] = ta.EMA(informative_1w, timeperiod=8)
        # informative_1w['fema_13'] = ta.EMA(informative_1w, timeperiod=13)
        # informative_1w['fema_21'] = ta.EMA(informative_1w, timeperiod=21)
        # informative_1w['fema_34'] = ta.EMA(informative_1w, timeperiod=34)
        # informative_1w['fema_55'] = ta.EMA(informative_1w, timeperiod=55)
        # informative_1w['fema_89'] = ta.EMA(informative_1w, timeperiod=89)
        # informative_1w['fema_144'] = ta.EMA(informative_1w, timeperiod=144)
        # informative_1w['fema_233'] = ta.EMA(informative_1w, timeperiod=233)

        # #HT_TRENDLINE Hilbert Transform - Instantaneous Trendline
        # informative_1w['ht_trendline'] = ta.HT_TRENDLINE(informative_1w)

        # #KAMA Kaufman Adaptive Moving Average
        informative_1w['kama_7'] = ta.KAMA(informative_1w, timeperiod=7)
        informative_1w['kama_25'] = ta.KAMA(informative_1w, timeperiod=25)
        informative_1w['kama_99'] = ta.KAMA(informative_1w, timeperiod=99)
        informative_1w['kama_200'] = ta.KAMA(informative_1w, timeperiod=200)
        informative_1w['kama_trend_up'] = informative_1w['kama_200'] > informative_1w['kama_200'].shift(1)
        informative_1w['kama_trend_down'] = informative_1w['kama_200'] < informative_1w['kama_200'].shift(1)


        # #MA Moving average


        # #MAMA MESA Adaptive Moving Average
        # informative_1w['mama'], informative_1w['fama'] = ta.MAMA(informative_1w)

        # #MAVP Moving average with variable period


        # #MIDPOINT MidPoint over period
        # informative_1w['midpoint_7'] = ta.MIDPOINT(informative_1w, timeperiod=7)
        # informative_1w['midpoint_25'] = ta.MIDPOINT(informative_1w, timeperiod=25)
        # informative_1w['midpoint_99'] = ta.MIDPOINT(informative_1w, timeperiod=99)
        # informative_1w['midpoint_200'] = ta.MIDPOINT(informative_1w, timeperiod=200)

        # #MIDPRICE Midpoint Price over period
        # informative_1w['midprice_7'] = ta.MIDPRICE(informative_1w, timeperiod=7)
        # informative_1w['midprice_25'] = ta.MIDPRICE(informative_1w, timeperiod=25)
        # informative_1w['midprice_99'] = ta.MIDPRICE(informative_1w, timeperiod=99)
        # informative_1w['midprice_200'] = ta.MIDPRICE(informative_1w, timeperiod=200)
        
        # #SAR Parabolic SAR
        informative_1w['sar'] = ta.SAR(informative_1w)

        # #SAREXT Parabolic SAR - Extended
        # informative_1w['sarext'] = ta.SAREXT(informative_1w)

        # #SMA Simple Moving Average
        # informative_1w['sma_7'] = ta.SMA(informative_1w, timeperiod=7)
        # informative_1w['sma_25'] = ta.SMA(informative_1w, timeperiod=25)
        # informative_1w['sma_99'] = ta.SMA(informative_1w, timeperiod=99)
        # informative_1w['sma_200'] = ta.SMA(informative_1w, timeperiod=200)

        # #T3 Triple Exponential Moving Average (T3)
        # informative_1w['t3_7'] = ta.T3(informative_1w, timeperiod=7)
        # informative_1w['t3_25'] = ta.T3(informative_1w, timeperiod=25)
        # informative_1w['t3_99'] = ta.T3(informative_1w, timeperiod=99)
        # informative_1w['t3_200'] = ta.T3(informative_1w, timeperiod=200)

        # #TEMA Triple Exponential Moving Average
        # informative_1w['tema_7'] = ta.TEMA(informative_1w, timeperiod=20)
        # informative_1w['tema_25'] = ta.TEMA(informative_1w, timeperiod=25)
        # informative_1w['tema_99'] = ta.TEMA(informative_1w, timeperiod=99)
        # informative_1w['tema_200'] = ta.TEMA(informative_1w, timeperiod=200)

        # #TRIMA Triangular Moving Average
        # informative_1w['trima_7'] = ta.TRIMA(informative_1w, timeperiod=7)
        # informative_1w['trima_25'] = ta.TRIMA(informative_1w, timeperiod=25)
        # informative_1w['trima_99'] = ta.TRIMA(informative_1w, timeperiod=99)
        # informative_1w['trima_200'] = ta.TRIMA(informative_1w, timeperiod=200)

        # #WMA Weighted Moving Average
        # informative_1w['wma_7'] = ta.WMA(informative_1w, timeperiod=7)
        # informative_1w['wma_25'] = ta.WMA(informative_1w, timeperiod=25)
        # informative_1w['wma_99'] = ta.WMA(informative_1w, timeperiod=99)
        # informative_1w['wma_200'] = ta.WMA(informative_1w, timeperiod=200)

        # #ADX Average Directional Movement Index
        informative_1w['adx'] = ta.ADX(informative_1w)

        # #ADXR Average Directional Movement Index Rating
        # informative_1w['adxr'] = ta.ADXR(informative_1w)

        # #APO Absolute Price Oscillator
        # informative_1w['apo'] = ta.APO(informative_1w)

        # #AROON Aroon

        # #AROONOSC Aroon Oscillator
        # informative_1w['aroonosc'] = ta.AROONOSC(informative_1w)

        # #BOP Balance Of Power
        # informative_1w['bop'] = ta.BOP(informative_1w)

        # #CCI Commodity Channel Index
        informative_1w['cci'] = ta.CCI(informative_1w)

        # #CMO Chande Momentum Oscillator
        # informative_1w['cmo'] = ta.CMO(informative_1w)

        # #DX Directional Movement Index
        # informative_1w['dx'] = ta.DX(informative_1w)

        # #MACD Moving Average Convergence/Divergence
        macd, macdsignal, macdhist = ta.MACD(informative_1w)
        informative_1w['macd'] = macd
        informative_1w['macdsignal'] = macdsignal
        informative_1w['macdhist'] = macdhist

        # #MACDEXT MACD with controllable MA type
        # informative_1w['macdext'], _, _ = ta.MACDEXT(informative_1w)
        
        # #MACDFIX Moving Average Convergence/Divergence Fix 12/26
        # informative_1w['macdfix'], _, _ = ta.MACDFIX(informative_1w)

        # #MFI Money Flow Index
        informative_1w['mfi'] = ta.MFI(informative_1w)

        # #MINUS_DI Minus Directional Indicator
        informative_1w['minus_di'] = ta.MINUS_DI(informative_1w)

        # #MINUS_DM Minus Directional Movement
        # informative_1w['minus_dm'] = ta.MINUS_DM(informative_1w)

        # #MOM Momentum
        # informative_1w['mom'] = ta.MOM(informative_1w)

        # #PLUS_DI Plus Directional Indicator
        informative_1w['plus_di'] = ta.PLUS_DI(informative_1w)

        # #PLUS_DM Plus Directional Movement
        # informative_1w['plus_dm'] = ta.PLUS_DM(informative_1w)

        # #PPO Percentage Price Oscillator
        # informative_1w['ppo'] = ta.PPO(informative_1w)

        # #ROC Rate of change : ((price/prevPrice)-1)*100
        informative_1w['roc'] = ta.ROC(informative_1w)

        # #ROCP Rate of change Percentage: (price-prevPrice)/prevPrice
        # informative_1w['rocp'] = ta.ROCP(informative_1w)

        # #ROCR Rate of change ratio: (price/prevPrice)
        # informative_1w['rocr'] = ta.ROCR(informative_1w)

        # #ROCR100 Rate of change ratio 100 scale: (price/prevPrice)*100
        # informative_1w['rocr100'] = ta.ROCR100(informative_1w)

        # #RSI Relative Strength Index
        informative_1w['rsi_3'] = ta.RSI(informative_1w,timeperiod=3)
        informative_1w['rsi_5'] = ta.RSI(informative_1w,timeperiod=5)
        informative_1w['rsi_8'] = ta.RSI(informative_1w,timeperiod=8)
        informative_1w['rsi_13'] = ta.RSI(informative_1w,timeperiod=13)
        informative_1w['rsi_21'] = ta.RSI(informative_1w,timeperiod=21)
        informative_1w['rsi_34'] = ta.RSI(informative_1w,timeperiod=34)

        # #STOCH Stochastic
        # slowk, slowd = ta.STOCH(informative_1w)
        # informative_1w['stoch_k'] = slowk
        # informative_1w['stoch_d'] = slowd

        # #STOCHF Stochastic Fast
        # fastk, fastd = ta.STOCHF(informative_1w)
        # informative_1w['stochf_k'] = fastk
        # informative_1w['stochf_d'] = fastd
        
        # #STOCHRSI Stochastic Relative Strength Index
        # informative_1w['stochrsi_k'], informative_1w['stochrsi_d'] = ta.STOCHRSI(informative_1w)

        # #TRIX 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        informative_1w['trix'] = ta.TRIX(informative_1w)

        # #ULTOSC Ultimate Oscillator
        # informative_1w['ultosc'] = ta.ULTOSC(informative_1w)

        # #WILLR Williams' %R
        # informative_1w['willr'] = ta.WILLR(informative_1w)

        # #AD Chaikin A/D Line
        # informative_1w['ad'] = ta.AD(informative_1w)

        # #ADOSC Chaikin A/D Oscillator
        # informative_1w['adosc'] = ta.ADOSC(informative_1w)

        # #OBV On Balance Volume
        informative_1w['obv'] = ta.OBV(informative_1w)

        # #ATR Average True Range
        # informative_1w['atr'] = ta.ATR(informative_1w)

        # #NATR Normalized Average True Range
        # informative_1w['natr'] = ta.NATR(informative_1w)

        # #TRANGE True Range
        # informative_1w['trange'] = ta.TRANGE(informative_1w)

        # #AVGPRICE Average Price
        # informative_1w['avgprice'] = ta.AVGPRICE(informative_1w)

        # #MEDPRICE Median Price
        # informative_1w['medprice'] = ta.MEDPRICE(informative_1w)

        # #TYPPRICE Typical Price
        # informative_1w['typprice'] = ta.TYPPRICE(informative_1w)

        # #WCLPRICE Weighted Close Price
        # informative_1w['wclprice'] = ta.WCLPRICE(informative_1w)

        # #HT_DCPERIOD Hilbert Transform - Dominant Cycle Period
        informative_1w['ht_dcperiod'] = ta.HT_DCPERIOD(informative_1w)

        # #HT_DCPHASE Hilbert Transform - Dominant Cycle Phase
        # informative_1w['ht_dcphase'] = ta.HT_DCPHASE(informative_1w)

        # #HT_PHASOR Hilbert Transform - Phasor Components
        # informative_1w['ht_phasor_inphase'], informative_1w['ht_phasor_quadrature'] = ta.HT_PHASOR(informative_1w)

        # #HT_SINE Hilbert Transform - SineWave
        # informative_1w['ht_sine'], informative_1w['ht_leadsine'] = ta.HT_SINE(informative_1w)

        # #HT_TRENDMODE Hilbert Transform - Trend vs Cycle Mode
        # informative_1w['ht_trendmode'] = ta.HT_TRENDMODE(informative_1w)

        dataframe = merge_informative_pair(dataframe, informative_1h, self.timeframe, '1h', ffill=True)
        dataframe = merge_informative_pair(dataframe, informative_4h, self.timeframe, '4h', ffill=True)
        dataframe = merge_informative_pair(dataframe, informative_1d, self.timeframe, '1d', ffill=True)
        dataframe = merge_informative_pair(dataframe, informative_1w, self.timeframe, '1w', ffill=True)

        return dataframe

    def assign_trend_type(self, dataframe: DataFrame) -> DataFrame:
        dataframe['trend_type'] = 'none'

        scalp_cond = (
            (dataframe['rsi_8'] < 30) & (dataframe['rsi_8'] > dataframe['rsi_8'].shift(1)) &
            (dataframe['ema_7'] > dataframe['ema_25']) &
            (dataframe['macd'] > dataframe['macdsignal']) &
            (dataframe['adx'] > 20) & (dataframe['plus_di'] > dataframe['minus_di'])
        )

        swing_cond = (
            (dataframe['ema_50_4h'] > dataframe['close']) &
            (dataframe['bbands_breakout_up_4h']) &
            (dataframe['rsi_13_4h'] > 40) &
            (dataframe['macd_4h'] > dataframe['macdsignal_4h'])
        )

        long_cond = (
            (dataframe['ema_99_1d'] > dataframe['close']) &
            (dataframe['macd_histogram_1d'] > 0) &
            (dataframe['rsi_13_1d'] > 55)
        )

        trend_cond = (
            (dataframe['ema_200_1w'] > dataframe['close']) &
            (dataframe['adx_1w'] > 25) &
            (dataframe['obv_1w'] > 0)
        )

        dataframe.loc[scalp_cond, 'trend_type'] = 'scalp'
        dataframe.loc[swing_cond, 'trend_type'] = 'swing'
        dataframe.loc[trend_cond, 'trend_type'] = 'trend'
        dataframe.loc[long_cond, 'trend_type'] = 'long'

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populates the 'enter_long' and 'enter_tag' columns based on trend_type.
        Ensures compatibility with Freqtrade UI for visibility of entry signals.
        """
        dataframe = self.assign_trend_type(dataframe)

        # Initialize columns
        dataframe['enter_long'] = 0
        dataframe['enter_tag'] = None

        # Scalping Entry
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'scalp') &
                (dataframe['volume'] > dataframe['volume'].rolling(20).mean()) &
                (dataframe['close'] > dataframe['ema_7'])
            ),
            ['enter_long', 'scalp_entry']
        ] = (1, 'scalp_entry')

        # Swing Entry
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'swing') &
                (dataframe['rsi_13_4h'] > 50) &
                (dataframe['macd_4h'] > dataframe['macdsignal_4h'])
            ),
            ['enter_long', 'swing_entry']
        ] = (1, 'swing_entry')

        # Long-Term Entry
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'long') &
                (dataframe['rsi_13_1d'] > 60) &
                (dataframe['macd_histogram_1d'] > 0)
            ),
            ['enter_long', 'long_entry']
        ] = (1, 'long_entry')

        # Trend-Following Entry
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'trend') &
                (dataframe['obv_1w'] > dataframe['obv_1w'].rolling(5).mean()) &
                (dataframe['adx_1w'] > 30)
            ),
            ['enter_long', 'trend_entry']
        ] = (1, 'trend_entry')

        return dataframe


    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Populates the 'exit_long' and 'exit_tag' columns with detailed logic for exits
        per strategy type: scalping, swing, long, and trend-following.
        """
        dataframe = self.assign_trend_type(dataframe)

        dataframe['exit_long'] = 0
        dataframe['exit_tag'] = None

        # === Scalping Exit ===
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'scalp') &
                (
                    (dataframe['ema_7'] < dataframe['ema_25']) |  # EMA 5 < EMA 13
                    (dataframe['sar'] > dataframe['close']) |  # SAR flip iznad sveće
                    (dataframe['bbands_breakout_down']) |  # BBANDS breakout down
                    ((dataframe['rsi_3'] > 70) & (dataframe['rsi_3'] < dataframe['rsi_3'].shift(1))) |
                    ((dataframe['cci'] > 100) & (dataframe['cci'] < dataframe['cci'].shift(1))) |
                    (dataframe['mfi'] > 80) |
                    ((dataframe['adx'] > 20) & (dataframe['minus_di'] > dataframe['plus_di']))
                )
            ),
            ['exit_long', 'exit_tag']
        ] = (1, 'scalp_exit')

        # === Swing Exit ===
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'swing') &
                (
                    (dataframe['ema_50_4h'] < dataframe['close']) |  # EMA50 acting as resistance
                    (dataframe['bbands_breakout_down_4h']) |  # BBANDS breakout down
                    (dataframe['kama_trend_down_4h']) |  # KAMA okrenut nadole (pretpostavimo da postoji ta kolona)
                    (dataframe['rsi_13_4h'] < 60) |
                    (dataframe['macd_4h'] < dataframe['macdsignal_4h']) |
                    (dataframe['obv_4h'] < dataframe['obv_4h'].shift(1)) |  # OBV pada
                    (dataframe['trix_4h'] < 0)
                )
            ),
            ['exit_long', 'exit_tag']
        ] = (1, 'swing_exit')

        # === Long Term Exit ===
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'long') &
                (
                    (dataframe['ema_200_1d'] < dataframe['close']) |  # EMA200 kao otpor
                    (dataframe['sar_1d'] > dataframe['close']) |
                    (dataframe['bbands_breakout_down_1d']) |
                    (dataframe['mfi_1d'] < 80) |
                    (dataframe['macd_histogram_1d'] < 0) |
                    (dataframe['roc_1d'] < 0)
                )
            ),
            ['exit_long', 'exit_tag']
        ] = (1, 'long_exit')

        # === Trend Exit ===
        dataframe.loc[
            (
                (dataframe['trend_type'] == 'trend') &
                (
                    (dataframe['ema_200_1w'] < dataframe['close']) |
                    (dataframe['kama_trend_down_1w']) |  # Ili MAMA — pretpostavimo da postoji
                    ((dataframe['adx_1w'] > 25) & (dataframe['minus_di_1w'] > dataframe['plus_di_1w'])) |
                    (dataframe['obv_1w'] < dataframe['obv_1w'].shift(1)) |
                    (dataframe['ht_dcperiod_1w'] > dataframe['ht_dcperiod_1w'].shift(1))  # momentum opada
                )
            ),
            ['exit_long', 'exit_tag']
        ] = (1, 'trend_exit')

        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime, current_rate: float, current_profit: float, **kwargs) -> float:
        # Dohvati poslednji poznati red iz DataProvider-a
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if dataframe is None or len(dataframe) < 1:
            return 1  # ne prekidaj

        last_candle = dataframe.iloc[-1]

        if last_candle['custom_stop_keep']:
            return 1  # Drži poziciju

        # Panic exit logika (dodaj ako želiš više signala)
        if last_candle['rsi_13_1h'] < 30 and last_candle['macd_histogram_1h'] < 0:
            return 0.98  # Stop-out na -2%

        return 0.95  # Fallback SL
