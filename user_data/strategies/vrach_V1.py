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
    inf_timeframes = {
        '1h': '1h',
        '4h': '4h',
        '1d': '1d'
    }
    
    startup_candle_count: int = 400

    # Dynamic ROI disabled, using custom_exit
    minimal_roi = {"0": 100}

    # Use custom stoploss
    stoploss = -0.99

    # Trailing stop handled manually in custom_stoploss
    trailing_stop = False

    use_custom_stoploss = True
    use_exit_signal = True
    process_only_new_candles = True
    ignore_buying_expired_candle_after = 5
    position_adjustment_enable = False

    def informative_pairs(self):
        pairs = [(pair, tf) for pair in self.dp.current_whitelist() for tf in self.inf_timeframes]
        return pairs  

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        #Normal Time Frame

        #TA-Lib
        # Momentum Indicators
        # ULTOSC               Ultimate Oscillator
        dataframe['ultosc'] = ta.ULTOSC(dataframe)
        # ADX
        dataframe['adx_14'] = ta.ADX(dataframe,timeperiod=14)
        #RSI                  Relative Strength Index
        dataframe['rsi_14'] = ta.RSI(dataframe,timeperiod=14)
        # Volume Indicators
        # OBV                  On Balance Volume
        dataframe['obv'] = ta.OBV(dataframe)
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd_hist'] = macd['macdhist']

        # Volatility Indicators
        # ATR                  Average True Range
        dataframe['atr'] = ta.ATR(dataframe)
        dataframe['atr_14'] = ta.ATR(dataframe,timeperiod=14)
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
        vortex = pta.vortex(dataframe['high'], dataframe['low'], dataframe['close'], length=14)
        dataframe['vtx_p'] = vortex['VTXP_14']
        dataframe['vtx_m'] = vortex['VTXM_14']

        # Proveri da nisu svi NaN
        if 'VTXP_14' in vortex and 'VTXM_14' in vortex:
            dataframe['vtx_gap'] = vortex['VTXP_14'] - vortex['VTXM_14']
        else:
            dataframe['vtx_gap'] = 0

        #Donchian
        donchian = pta.donchian(dataframe['high'],dataframe['low'],20,20)
        dataframe['dcl_20'] = donchian['DCL_20_20']
        dataframe['dcm_20'] = donchian['DCM_20_20']
        dataframe['dcu_20'] = donchian['DCU_20_20']

        #Massi
        massi = pta.massi(dataframe['high'],dataframe['low'],9,25)
        dataframe['massi'] = massi 
 
        #RVI Indicator: Relative Volatility Index (RVI)
        dataframe['rvi_14'] = pta.rvi(dataframe,lenght=14)

        #CMF Chaikin Money Flow 
        dataframe['cmf_20'] = pta.cmf(dataframe['high'],dataframe['low'],dataframe['close'],dataframe['volume'],lenght=20)

        #EBSW Even Better SineWave (EBSW)
        dataframe['ebsw'] = pta.ebsw(dataframe['close'],lenght=40,bars=10)

        for tf in self.inf_timeframes.values():
            informative = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=tf)
            informative[f'ema_50_{tf}'] = ta.EMA(informative, timeperiod=50)
            informative[f'ema_200_{tf}'] = ta.EMA(informative, timeperiod=200)
            informative[f'adx_{tf}'] = ta.ADX(informative, timeperiod=14)
            dataframe = merge_informative_pair(dataframe, informative, self.timeframe, tf, ffill=True)

        return dataframe


    def multi_tf_market_scoring(self, pair: str) -> dict:
        """
        Višetimeframe analiza tržišta sa višeslojnim skoringom i pozicionim preporukama.
        
        Timeframe-ovi: 1h, 4h, 1d
        Score nivoi: Trend, Momentum, Volatility, Structure, Final

        :return: Dict sa score-ovima po TF + globalna preporuka pozicije
        """
        import talib.abstract as ta
        tf_weights = {'1h': 0.3, '4h': 0.4, '1d': 0.3}
        timeframes = ['1h', '4h', '1d']

        final_scores = {}
        composite_score = 0

        for tf in timeframes:
            df, _ = self.dp.get_analyzed_dataframe(pair, tf)
            if df is None or len(df) < 200:
                final_scores[tf] = {"L1": 0, "L2": 0, "L3": 0, "L4": 0, "L5": 0}
                continue

            df = df.copy()
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']

            # Indikatori
            ema200 = ta.EMA(df, timeperiod=200)
            ema50 = ta.EMA(df, timeperiod=50)
            rsi = ta.RSI(df, timeperiod=14)
            macd, macdsignal, _ = ta.MACD(df)
            atr = ta.ATR(df, timeperiod=14)
            bb_upper, bb_middle, bb_lower = ta.BBANDS(close, timeperiod=20)
            bb_width = bb_upper - bb_lower

            # L1: Trend Strength
            ema_slope = ema200.iloc[-1] - ema200.iloc[-5]
            trend_score = min(max((ema_slope / close.iloc[-1]) * 1000, 0), 100)
            if close.iloc[-1] > ema200.iloc[-1]:
                trend_score += 20
            trend_score = min(trend_score, 100)

            # L2: Momentum Strength
            rsi_score = max(min((rsi.iloc[-1] - 50) * 2, 100), 0)
            macd_score = max(min((macd.iloc[-1] - macdsignal.iloc[-1]) * 200, 100), 0)
            momentum_score = int((rsi_score + macd_score) / 2)

            # L3: Volatility State
            volatility = bb_width.iloc[-1] / close.iloc[-1]
            if volatility > 0.08:
                vol_score = 90
            elif volatility > 0.05:
                vol_score = 60
            elif volatility > 0.02:
                vol_score = 30
            else:
                vol_score = 10

            # L4: Structure (Price Action)
            hh = close.iloc[-1] > close.iloc[-5]
            hl = low.iloc[-1] > low.iloc[-5]
            structure_score = 0
            if hh: structure_score += 50
            if hl: structure_score += 50

            # L5: Final Score (po TF)
            total_score = (trend_score * 0.3 + momentum_score * 0.3 +
                        vol_score * 0.2 + structure_score * 0.2)
            total_score = int(total_score)

            final_scores[tf] = {
                "L1_Trend": int(trend_score),
                "L2_Momentum": int(momentum_score),
                "L3_Volatility": int(vol_score),
                "L4_Structure": int(structure_score),
                "L5_Final": int(total_score)
            }

            # Učestvuje u kompozitnom skoru
            composite_score += total_score * tf_weights[tf]

        # Finalna preporuka za veličinu pozicije (0.0 do 1.0)
        position_size = round(min(composite_score / 100, 1.0), 2)

        return {
            "scores": final_scores,
            "composite_score": int(composite_score),
            "position_size": position_size
        }

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:


        return dataframe


    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                        current_profit: float, **kwargs) -> float:
        """
        Napredna trailing stop loss logika koja se prilagođava tržišnom stanju i koristi score za dinamičku kontrolu rizika.

        :param pair: str - valutni par
        :param trade: Trade - aktivna pozicija
        :param current_time: datetime
        :param current_rate: float
        :param current_profit: float
        :return: float - nova stop loss cena (ili 1.0 da se ne menja)
        """

        # Preuzmi stanje tržišta i para (npr. iz koda: self.market_conditions = get_market_conditions(...))
        market_cond = self.market_conditions.get('market', {})
        pair_cond = self.market_conditions.get(pair, {})

        # Default vrednosti ako nije definisano
        market_score = market_cond.get('score', 0)
        pair_score = pair_cond.get('score', 0)
        trend = pair_cond.get('trend', 'neutral')  # uptrend / downtrend / ranging
        volatility = pair_cond.get('volatility', 0.01)  # npr. 1% dnevna promena

        # 1. Dinamični prag za aktivaciju trailing SL
        base_activation_profit = 0.01  # 1%
        score_bonus = (pair_score + market_score) / 200  # vrednost 0.0 - 1.0
        activation_profit_pct = base_activation_profit + (score_bonus * 0.015)  # do 2.5%

        if current_profit < activation_profit_pct:
            return 1.0  # ne aktiviraj još

        # 2. Trailing distanca zavisi od volatilnosti i trenda
        atr_period = 14
        atr_mult = 1.5 + (1 - score_bonus)  # bolji score = manji buffer
        min_trailing_pct = 0.003 + (0.01 - volatility) * 0.5  # adaptivno smanji za nisku volatilnost

        # Dobavi analizirani dataframe
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or len(dataframe) < atr_period:
            return 1.0

        # Izračunaj ATR trailing distancu
        atr = ta.ATR(dataframe, timeperiod=atr_period).iloc[-1]
        trail_dist = max(current_rate * min_trailing_pct, atr_mult * atr)

        # 3. Predlog novog stop loss nivoa
        new_stop = current_rate - trail_dist

        # 4. Hard floor - zavisi od trenda i score-a
        if trend == 'downtrend' or score_bonus < 0.3:
            hard_floor_enabled = True
        else:
            hard_floor_enabled = False

        if hard_floor_enabled:
            new_stop = max(new_stop, trade.open_rate * 1.001)

        # 5. Ako već imamo SL, koristi višu vrednost
        if trade.stop_loss:
            new_stop = max(new_stop, trade.stop_loss)

        return new_stop / trade.open_rate


    def calculate_stake(self, pair: str) -> float:
        """
        Izračunava koliki deo kapitala da uloži na osnovu višetimeframe market scoring-a.

        Vraća vrednost između 0.0 (bez ulaza) i 1.0 (maksimalni ulog).
        """

        market_scores = self.multi_tf_market_scoring(pair)
        score = market_scores.get('composite_score', 0)

        # Pragovi i stake % (ovo možeš optimizovati ili hyperopt-ovati)
        if score >= 80:
            stake = 1.0     # Full stake
        elif score >= 60:
            stake = 0.6     # Srednji ulog
        elif score >= 40:
            stake = 0.3     # Mali ulog
        else:
            stake = 0.0     # Ne ulazi u poziciju

        return stake
