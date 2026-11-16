import unittest
from analyze import wilson_interval
from collector import BASE

class ResearchTests(unittest.TestCase):
    def test_empty_interval(self):
        self.assertEqual(wilson_interval(0,0),[None,None])
    def test_interval_bounds(self):
        low,high=wilson_interval(2,100)
        self.assertLessEqual(low,0.02)
        self.assertGreaterEqual(high,0.02)
    def test_read_only_base(self):
        self.assertTrue(BASE.startswith('https://'))

if __name__=='__main__':unittest.main()
