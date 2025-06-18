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

    minimal_roi = {}
    stoploss = -0.99
    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True
    use_custom_stoploss = False
    use_custom_exit = False
    can_short = False
    process_only_new_candles = True
    

    startup_candle_count = 288

    inf_timeframes = ['1h', '4h', '1d']

    def informative_pairs(self):
        pairs = [(pair, tf) for pair in self.dp.current_whitelist() for tf in self.inf_timeframes]
        return pairs

    def indicators_normal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        #TA-Lib
        
        # Overlap Studies
        # BBANDS               Bollinger Bands
        # DEMA                 Double Exponential Moving Average
        # EMA                  Exponential Moving Average
        # HT_TRENDLINE         Hilbert Transform - Instantaneous Trendline
        # KAMA                 Kaufman Adaptive Moving Average
        # MA                   Moving average
        # MAMA                 MESA Adaptive Moving Average
        # MAVP                 Moving average with variable period
        # MIDPOINT             MidPoint over period
        # MIDPRICE             Midpoint Price over period
        # SAR                  Parabolic SAR
        # SAREXT               Parabolic SAR - Extended
        # SMA                  Simple Moving Average
        # T3                   Triple Exponential Moving Average (T3)
        # TEMA                 Triple Exponential Moving Average
        # TRIMA                Triangular Moving Average
        # WMA                  Weighted Moving Average#Overlap Studies
        
        # Momentum Indicators
        # ADX                  Average Directional Movement Index
        # ADXR                 Average Directional Movement Index Rating
        # APO                  Absolute Price Oscillator
        # AROON                Aroon
        # AROONOSC             Aroon Oscillator
        # BOP                  Balance Of Power
        # CCI                  Commodity Channel Index
        # CMO                  Chande Momentum Oscillator
        # DX                   Directional Movement Index
        # MACD                 Moving Average Convergence/Divergence
        # MACDEXT              MACD with controllable MA type
        # MACDFIX              Moving Average Convergence/Divergence Fix 12/26
        # MFI                  Money Flow Index
        # MINUS_DI             Minus Directional Indicator
        # MINUS_DM             Minus Directional Movement
        # MOM                  Momentum
        # PLUS_DI              Plus Directional Indicator
        # PLUS_DM              Plus Directional Movement
        # PPO                  Percentage Price Oscillator
        # ROC                  Rate of change : ((price/prevPrice)-1)*100
        # ROCP                 Rate of change Percentage: (price-prevPrice)/prevPrice
        # ROCR                 Rate of change ratio: (price/prevPrice)
        # ROCR100              Rate of change ratio 100 scale: (price/prevPrice)*100
        # RSI                  Relative Strength Index
        # STOCH                Stochastic
        # STOCHF               Stochastic Fast
        # STOCHRSI             Stochastic Relative Strength Index
        # TRIX                 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        # ULTOSC               Ultimate Oscillator
        # WILLR                Williams' %R
 
        # Volume Indicators
        # AD                   Chaikin A/D Line
        # ADOSC                Chaikin A/D Oscillator
        # OBV                  On Balance Volume

        # Volatility Indicators
        # ATR                  Average True Range
        # NATR                 Normalized Average True Range
        # TRANGE               True Range

        # Price Transform
        # AVGPRICE             Average Price
        # MEDPRICE             Median Price
        # TYPPRICE             Typical Price
        # WCLPRICE             Weighted Close Price

        # Cycle Indicators
        # HT_DCPERIOD          Hilbert Transform - Dominant Cycle Period
        # HT_DCPHASE           Hilbert Transform - Dominant Cycle Phase
        # HT_PHASOR            Hilbert Transform - Phasor Components
        # HT_SINE              Hilbert Transform - SineWave
        # HT_TRENDMODE         Hilbert Transform - Trend vs Cycle Mode

        # Pattern Recognition
        # CDL2CROWS            Two Crows
        # CDL3BLACKCROWS       Three Black Crows
        # CDL3INSIDE           Three Inside Up/Down
        # CDL3LINESTRIKE       Three-Line Strike
        # CDL3OUTSIDE          Three Outside Up/Down
        # CDL3STARSINSOUTH     Three Stars In The South
        # CDL3WHITESOLDIERS    Three Advancing White Soldiers
        # CDLABANDONEDBABY     Abandoned Baby
        # CDLADVANCEBLOCK      Advance Block
        # CDLBELTHOLD          Belt-hold
        # CDLBREAKAWAY         Breakaway
        # CDLCLOSINGMARUBOZU   Closing Marubozu
        # CDLCONCEALBABYSWALL  Concealing Baby Swallow
        # CDLCOUNTERATTACK     Counterattack
        # CDLDARKCLOUDCOVER    Dark Cloud Cover
        # CDLDOJI              Doji
        # CDLDOJISTAR          Doji Star
        # CDLDRAGONFLYDOJI     Dragonfly Doji
        # CDLENGULFING         Engulfing Pattern
        # CDLEVENINGDOJISTAR   Evening Doji Star
        # CDLEVENINGSTAR       Evening Star
        # CDLGAPSIDESIDEWHITE  Up/Down-gap side-by-side white lines
        # CDLGRAVESTONEDOJI    Gravestone Doji
        # CDLHAMMER            Hammer
        # CDLHANGINGMAN        Hanging Man
        # CDLHARAMI            Harami Pattern
        # CDLHARAMICROSS       Harami Cross Pattern
        # CDLHIGHWAVE          High-Wave Candle
        # CDLHIKKAKE           Hikkake Pattern
        # CDLHIKKAKEMOD        Modified Hikkake Pattern
        # CDLHOMINGPIGEON      Homing Pigeon
        # CDLIDENTICAL3CROWS   Identical Three Crows
        # CDLINNECK            In-Neck Pattern
        # CDLINVERTEDHAMMER    Inverted Hammer
        # CDLKICKING           Kicking
        # CDLKICKINGBYLENGTH   Kicking - bull/bear determined by the longer marubozu
        # CDLLADDERBOTTOM      Ladder Bottom
        # CDLLONGLEGGEDDOJI    Long Legged Doji
        # CDLLONGLINE          Long Line Candle
        # CDLMARUBOZU          Marubozu
        # CDLMATCHINGLOW       Matching Low
        # CDLMATHOLD           Mat Hold
        # CDLMORNINGDOJISTAR   Morning Doji Star
        # CDLMORNINGSTAR       Morning Star
        # CDLONNECK            On-Neck Pattern
        # CDLPIERCING          Piercing Pattern
        # CDLRICKSHAWMAN       Rickshaw Man
        # CDLRISEFALL3METHODS  Rising/Falling Three Methods
        # CDLSEPARATINGLINES   Separating Lines
        # CDLSHOOTINGSTAR      Shooting Star
        # CDLSHORTLINE         Short Line Candle
        # CDLSPINNINGTOP       Spinning Top
        # CDLSTALLEDPATTERN    Stalled Pattern
        # CDLSTICKSANDWICH     Stick Sandwich
        # CDLTAKURI            Takuri (Dragonfly Doji with very long lower shadow)
        # CDLTASUKIGAP         Tasuki Gap
        # CDLTHRUSTING         Thrusting Pattern
        # CDLTRISTAR           Tristar Pattern
        # CDLUNIQUE3RIVER      Unique 3 River
        # CDLUPSIDEGAP2CROWS   Upside Gap Two Crows
        # CDLXSIDEGAP3METHODS  Upside/Downside Gap Three Methods

        # Statistic Functions
        # BETA                 Beta
        # CORREL               Pearson's Correlation Coefficient (r)
        # LINEARREG            Linear Regression
        # LINEARREG_ANGLE      Linear Regression Angle
        # LINEARREG_INTERCEPT  Linear Regression Intercept
        # LINEARREG_SLOPE      Linear Regression Slope
        # STDDEV               Standard Deviation
        # TSF                  Time Series Forecast
        # VAR                  Variance

        #Pandas TA

        #Zero Lag Moving Average: zlma
        #Vortex: vortex


        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Scalping Entry
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['close_quant_low_01']) &
                #(dataframe['adx'] < 20) &  # znači da je range
                (dataframe['rsi_13'] < dataframe['rsi_13_quant_low_02']) &  # preprodato
                (dataframe['volume'] > dataframe['volume'].rolling(20).mean())
            ),
            ['enter_long', 'enter_tag']
        ] = (1, 'scalp_max_confirmed')

        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Scalping Exit
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['close_quant_high_99']) &
                (dataframe['close'] > dataframe['high']*0.995)
            ),
            ['exit_long', 'exit_tag']
        ] = (1, 'scalp_max_confirmed')
        return dataframe
