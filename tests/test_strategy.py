import unittest
from strategy.cooldown import eligible
from strategy.one_cent_strategy import signals
from backtesting.performance import summarize


class StrategyTests(unittest.TestCase):
    def test_cooldown_boundary(self):
        self.assertFalse(eligible(60, 10, 50))
        self.assertTrue(eligible(61, 10, 50))

    def test_signal_excludes_reversal(self):
        rows = [
            {'interval_index': '1', 'reversal': '1'},
            {'interval_index': '2', 'reversal': '0'},
            {'interval_index': '3', 'reversal': '0'},
        ]
        self.assertEqual([r['interval_index'] for r in signals(rows, 1)], ['3'])

    def test_payoff(self):
        result = summarize([{'yes_settled': '1'}, {'yes_settled': '0'}])
        self.assertEqual(result['pnl_usd'], 0.98)


if __name__ == '__main__':
    unittest.main()
