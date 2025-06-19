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
import numpy as np
import pandas as pd
import pandas_ta as pta
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
    use_custom_stoploss = True
    use_custom_exit = True
    can_short = False
    process_only_new_candles = True
    startup_candle_count = 288

    inf_timeframes = ['1h', '4h', '1d']
    inf_1h = '1h'
    inf_4h = '4h'
    inf_1d = '1d'

    def informative_pairs(self):
        pairs = [(pair, tf) for pair in self.dp.current_whitelist() for tf in self.inf_timeframes]
        return pairs

    def informative_1d_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        assert self.dp, "DataProvider is required for multiple timeframes."
        # Get the informative pair
        informative_1d = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=self.inf_1d)
        
        #TA-Lib
        # Momentum Indicators
        # ULTOSC               Ultimate Oscillator
        informative_1d['ultosc'] = ta.ULTOSC(informative_1d)
 
        # Volume Indicators
        # OBV                  On Balance Volume
        informative_1d['obv'] = ta.OBV(informative_1d)

        # Volatility Indicators
        # ATR                  Average True Range
        informative_1d['atr'] = ta.ATR(informative_1d)
        # NATR                 Normalized Average True Range
        informative_1d['natr'] = ta.NATR(informative_1d)

        #Pandas TA
        #Zero Lag Moving Average: zlma
        informative_1d['zlma_12'] = pta.zlma(informative_1d['close'], length=12)
        informative_1d['zlma_20'] = pta.zlma(informative_1d['close'], length=20)
        informative_1d['zlma_26'] = pta.zlma(informative_1d['close'], length=26)
        informative_1d['zlma_50'] = pta.zlma(informative_1d['close'], length=50)
        informative_1d['zlma_100'] = pta.zlma(informative_1d['close'], length=100)
        informative_1d['zlma_200'] = pta.zlma(informative_1d['close'], length=200)

        #Vortex: vortex
        vortex = pta.vortex(informative_1d['high'],informative_1d['low'],informative_1d['close'],14)
        informative_1d['vtx_p'] = vortex['VTXP_14']
        informative_1d['vtx_m'] = vortex['VTXM_14']
        informative_1d['vtx_gap'] = informative_1d['vtx_p'] - informative_1d['vtx_m']

        #Donchian
        donchian = pta.donchian(informative_1d['high'],informative_1d['low'],20,20)
        informative_1d['DCL_20'] = donchian['DCL_20_20']
        informative_1d['DCM_20'] = donchian['DCM_20_20']
        informative_1d['DCU_20'] = donchian['DCU_20_20']

        #Massi
        massi = pta.massi(informative_1d['high'],informative_1d['low'],9,25)
        informative_1d['massi'] = massi 
 
        #RVI Indicator: Relative Volatility Index (RVI)
        informative_1d['rvi_14'] = pta.rvi(informative_1d,lenght=14)

        #CMF Chaikin Money Flow 
        informative_1d['cmf_20'] = pta.cmf(informative_1d['high'],informative_1d['low'],informative_1d['close'],informative_1d['volume'],lenght=20)

        #EBSW Even Better SineWave (EBSW)
        informative_1d['ebsw'] = pta.ebsw(informative_1d,lenght=40,bars=10)

        return dataframe

    def informative_4h_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        assert self.dp, "DataProvider is required for multiple timeframes."
        # Get the informative pair
        informative_4h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=self.inf_4h)
        
        #TA-Lib
        # Momentum Indicators
        # ULTOSC               Ultimate Oscillator
        informative_4h['ultosc'] = ta.ULTOSC(informative_4h)
 
        # Volume Indicators
        # OBV                  On Balance Volume
        informative_4h['obv'] = ta.OBV(informative_4h)

        # Volatility Indicators
        # ATR                  Average True Range
        informative_4h['atr'] = ta.ATR(informative_4h)
        # NATR                 Normalized Average True Range
        informative_4h['natr'] = ta.NATR(informative_4h)

        #Pandas TA
        #Zero Lag Moving Average: zlma
        informative_4h['zlma_12'] = pta.zlma(informative_4h['close'], length=12)
        informative_4h['zlma_20'] = pta.zlma(informative_4h['close'], length=20)
        informative_4h['zlma_26'] = pta.zlma(informative_4h['close'], length=26)
        informative_4h['zlma_50'] = pta.zlma(informative_4h['close'], length=50)
        informative_4h['zlma_100'] = pta.zlma(informative_4h['close'], length=100)
        informative_4h['zlma_200'] = pta.zlma(informative_4h['close'], length=200)

        #Vortex: vortex
        vortex = pta.vortex(informative_4h['high'],informative_4h['low'],informative_4h['close'],14)
        informative_4h['vtx_p'] = vortex['VTXP_14']
        informative_4h['vtx_m'] = vortex['VTXM_14']
        informative_4h['vtx_gap'] = informative_4h['vtx_p'] - informative_4h['vtx_m']

        #Donchian
        donchian = pta.donchian(informative_4h['high'],informative_4h['low'],20,20)
        informative_4h['DCL_20'] = donchian['DCL_20_20']
        informative_4h['DCM_20'] = donchian['DCM_20_20']
        informative_4h['DCU_20'] = donchian['DCU_20_20']

        #Massi
        massi = pta.massi(informative_4h['high'],informative_4h['low'],9,25)
        informative_4h['massi'] = massi 
 
        #RVI Indicator: Relative Volatility Index (RVI)
        informative_4h['rvi_14'] = pta.rvi(informative_4h,lenght=14)

        #CMF Chaikin Money Flow 
        informative_4h['cmf_20'] = pta.cmf(informative_4h['high'],informative_4h['low'],informative_4h['close'],informative_4h['volume'],lenght=20)

        #EBSW Even Better SineWave (EBSW)
        informative_4h['ebsw'] = pta.ebsw(informative_4h,lenght=40,bars=10)

        return dataframe

    def informative_1h_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        assert self.dp, "DataProvider is required for multiple timeframes."
        # Get the informative pair
        informative_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=self.inf_1h)
        
        #TA-Lib
        # Momentum Indicators
        # ULTOSC               Ultimate Oscillator
        informative_1h['ultosc'] = ta.ULTOSC(informative_1h)
 
        # Volume Indicators
        # OBV                  On Balance Volume
        informative_1h['obv'] = ta.OBV(informative_1h)

        # Volatility Indicators
        # ATR                  Average True Range
        informative_1h['atr'] = ta.ATR(informative_1h)
        # NATR                 Normalized Average True Range
        informative_1h['natr'] = ta.NATR(informative_1h)

        #Pandas TA
        #Zero Lag Moving Average: zlma
        informative_1h['zlma_12'] = pta.zlma(informative_1h['close'], length=12)
        informative_1h['zlma_20'] = pta.zlma(informative_1h['close'], length=20)
        informative_1h['zlma_26'] = pta.zlma(informative_1h['close'], length=26)
        informative_1h['zlma_50'] = pta.zlma(informative_1h['close'], length=50)
        informative_1h['zlma_100'] = pta.zlma(informative_1h['close'], length=100)
        informative_1h['zlma_200'] = pta.zlma(informative_1h['close'], length=200)

        #Vortex: vortex
        vortex = pta.vortex(informative_1h['high'],informative_1h['low'],informative_1h['close'],14)
        informative_1h['vtx_p'] = vortex['VTXP_14']
        informative_1h['vtx_m'] = vortex['VTXM_14']
        informative_1h['vtx_gap'] = informative_1h['vtx_p'] - informative_1h['vtx_m']

        #Donchian
        donchian = pta.donchian(informative_1h['high'],informative_1h['low'],20,20)
        informative_1h['DCL_20'] = donchian['DCL_20_20']
        informative_1h['DCM_20'] = donchian['DCM_20_20']
        informative_1h['DCU_20'] = donchian['DCU_20_20']

        #Massi
        massi = pta.massi(informative_1h['high'],informative_1h['low'],9,25)
        informative_1h['massi'] = massi 
 
        #RVI Indicator: Relative Volatility Index (RVI)
        informative_1h['rvi_14'] = pta.rvi(informative_1h,lenght=14)

        #CMF Chaikin Money Flow 
        informative_1h['cmf_20'] = pta.cmf(informative_1h['high'],informative_1h['low'],informative_1h['close'],informative_1h['volume'],lenght=20)

        #EBSW Even Better SineWave (EBSW)
        informative_1h['ebsw'] = pta.ebsw(informative_1h,lenght=40,bars=10)

        return dataframe

    def timeframe_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        #TA-Lib
        # Momentum Indicators
        # ULTOSC               Ultimate Oscillator
        dataframe['ultosc'] = ta.ULTOSC(dataframe)
 
        # Volume Indicators
        # OBV                  On Balance Volume
        dataframe['obv'] = ta.OBV(dataframe)

        # Volatility Indicators
        # ATR                  Average True Range
        dataframe['atr'] = ta.ATR(dataframe)
        # NATR                 Normalized Average True Range
        dataframe['natr'] = ta.NATR(dataframe)

        #Pandas TA
        #Zero Lag Moving Average: zlma
        dataframe['zlma_12'] = pta.zlma(dataframe['close'], length=12)
        dataframe['zlma_20'] = pta.zlma(dataframe['close'], length=20)
        dataframe['zlma_26'] = pta.zlma(dataframe['close'], length=26)
        dataframe['zlma_50'] = pta.zlma(dataframe['close'], length=50)
        dataframe['zlma_100'] = pta.zlma(dataframe['close'], length=100)
        dataframe['zlma_200'] = pta.zlma(dataframe['close'], length=200)

        #Vortex: vortex
        vortex = pta.vortex(dataframe['high'],dataframe['low'],dataframe['close'],14)
        dataframe['vtx_p'] = vortex['VTXP_14']
        dataframe['vtx_m'] = vortex['VTXM_14']
        dataframe['vtx_gap'] = dataframe['vtx_p'] - dataframe['vtx_m']

        #Donchian
        donchian = pta.donchian(dataframe['high'],dataframe['low'],20,20)
        dataframe['DCL_20'] = donchian['DCL_20_20']
        dataframe['DCM_20'] = donchian['DCM_20_20']
        dataframe['DCU_20'] = donchian['DCU_20_20']

        #Massi
        massi = pta.massi(dataframe['high'],dataframe['low'],9,25)
        dataframe['massi'] = massi 
 
        #RVI Indicator: Relative Volatility Index (RVI)
        dataframe['rvi_14'] = pta.rvi(dataframe,lenght=14)

        #CMF Chaikin Money Flow 
        dataframe['cmf_20'] = pta.cmf(dataframe['high'],dataframe['low'],dataframe['close'],dataframe['volume'],lenght=20)

        #EBSW Even Better SineWave (EBSW)
        dataframe['ebsw'] = pta.ebsw(dataframe,lenght=40,bars=10)

        return dataframe
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        informative_1h = self.informative_1h_indicators(dataframe, metadata)
        informative_4h = self.informative_4h_indicators(dataframe,metadata)
        informative_1d = self.informative_1d_indicators(dataframe,metadata)

        dataframe = merge_informative_pair(dataframe, informative_1h, self.timeframe, self.inf_1h, ffill=True)
        dataframe = merge_informative_pair(dataframe, informative_4h, self.timeframe, self.inf_4h, ffill=True)
        dataframe = merge_informative_pair(dataframe, informative_1d, self.timeframe, self.inf_1d, ffill=True)

        # The indicators for the normal (5m) timeframe
        dataframe = self.timeframe_indicators(dataframe, metadata)

        return dataframe



    def populate_position_score(self, dataframe: DataFrame) -> DataFrame:
        dataframe['score'] = 0

        # Macro trend alignment (daily ZLMA > 50)
        dataframe.loc[(dataframe['close_1d'] > dataframe['zlma_50_1d']), 'score'] += 2
        dataframe.loc[(dataframe['vtx_gap_4h'] > 0), 'score'] += 1
        dataframe.loc[(dataframe['ultosc'] > 50), 'score'] += 1
        dataframe.loc[(dataframe['cmf_20'] > 0), 'score'] += 1
        dataframe.loc[(dataframe['obv'] > dataframe['obv'].shift(1)), 'score'] += 1

        return dataframe

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: Optional[float] = None, **kwargs) -> float:
        """
        Dynamic leverage manager — adjusts exposure based on score.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        score = dataframe.iloc[-1]['score']

        if score >= 5:
            return 3.0  # Max risk
        elif score >= 3:
            return 2.0
        return 1.0

    def position_adjustment(self, trade: Trade, current_time: datetime,
                             current_rate: float, current_profit: float,
                             amount: float, **kwargs) -> Optional[float]:
        """
        Risk manager — adjusts size based on performance.
        """
        max_position = 100  # Cap per trade
        risk_factor = min(max(trade.pnl_percentage / 10, 0.5), 2.0)  # Adaptive risk control
        adjusted_size = min(amount * risk_factor, max_position)
        return adjusted_size

    def market_regime(self,dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        
        
        
        
        
        
        
        
        # # Scalping Entry
        # dataframe.loc[
        #     (
        #         (dataframe['close'] < dataframe['close_quant_low_01']) &
        #         #(dataframe['adx'] < 20) &  # znači da je range
        #         (dataframe['rsi_13'] < dataframe['rsi_13_quant_low_02']) &  # preprodato
        #         (dataframe['volume'] > dataframe['volume'].rolling(20).mean())
        #     ),
        #     ['enter_long', 'enter_tag']
        # ] = (1, 'scalp_max_confirmed')

        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # # Scalping Exit
        # dataframe.loc[
        #     (
        #         (dataframe['close'] > dataframe['close_quant_high_99']) &
        #         (dataframe['close'] > dataframe['high']*0.995)
        #     ),
        #     ['exit_long', 'exit_tag']
        # ] = (1, 'scalp_max_confirmed')
        return dataframe


    def custom_exit(self, pair: str, trade: Trade, current_time: datetime,
                    current_rate: float, current_profit: float, **kwargs) -> Optional[str]:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1]

        # Exit condition 1: price reached upper donchian band
        if current_rate >= last_candle['DCU_20']:
            return 'donchian_tp'

        # Exit condition 2: RVI shows volatility reversal
        if last_candle['rvi_14'] < 50:
            return 'rvi_exit'

        # Exit condition 3: Score collapsed
        if last_candle['score'] < 2:
            return 'score_drop_exit'

        return None

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        entry_index = dataframe.index.get_loc(trade.open_date_utc, method='nearest')
        atr = dataframe['atr'].iloc[entry_index]
        entry_low = dataframe['low'].iloc[entry_index]
        stop_price = entry_low - 1.5 * atr

        if current_rate <= stop_price:
            return 0.99  # Full stop

        return 1  # Hold position
