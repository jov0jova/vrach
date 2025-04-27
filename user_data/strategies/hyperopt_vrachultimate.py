from freqtrade.optimize.hyperopt import IHyperOpt
from freqtrade.optimize.space import Categorical, Dimension, Integer, Real

class VrachUltimateHyperopt(IHyperOpt):
    # Optimizacija samo za profit
    @staticmethod
    def hyperopt_loss_function(results: dict, trade_count: int, min_date: str, max_date: str, max_loss: float = 0.0) -> float:
        if results['profit_total_abs'] < 0:
            return 1000
        return -results['profit_total_abs']

    @staticmethod
    def generate_spaces() -> list:
        return [
            # ROI - kad i koliko profita zaključavamo
            Integer(1, 30, name='roi_t1'),
            Integer(10, 120, name='roi_t2'),
            Real(0.005, 0.05, name='roi_p1'),
            Real(0.001, 0.03, name='roi_p2'),

            # STOPLOSS
            Real(-0.05, -0.01, name='stoploss'),

            # Trailing
            Categorical([True, False], name='trailing_stop'),
            Real(0.005, 0.04, name='trailing_stop_positive'),
            Real(0.01, 0.05, name='trailing_stop_positive_offset')
        ]
