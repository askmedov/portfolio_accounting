import os
import sys
import unittest

import pandas as pd

package_path = '\\'.join(os.path.realpath(__file__).split('\\')[:-2])
sys.path.append(package_path)
from conventions import ACT_360

class TestACT_360(unittest.TestCase):
    
    def setUp(self):
        self.day_count = ACT_360()
        self.start_date = pd.to_datetime('2023-01-01')
        self.end_date = pd.to_datetime('2023-12-31')
        self.sf_leap = pd.to_datetime('2019-07-01')
        self.ed_leap = pd.to_datetime('2020-03-31')
        
    def test_numerators(self):
        # no maturity and inception
        day_count = ACT_360()
        self.assertEqual(day_count.numerator, 365)
        
        # maturity and inception outside of a leap year
        day_count = ACT_360(inception=pd.to_datetime('2017-07-01'), maturity=pd.to_datetime('2018-04-01'))
        self.assertEqual(day_count.numerator, 365)
        
        # maturity is exactly 1 leap year ahead
        day_count = ACT_360(inception=pd.to_datetime('2019-09-01'), maturity=pd.to_datetime('2020-09-01'))
        self.assertEqual(day_count.numerator, 366)
        
        # maturity is less than 1 year ahead and there is a leap day in the next 12 months
        day_count = ACT_360(inception=pd.to_datetime('2019-06-01'), maturity=pd.to_datetime('2019-09-01'))
        self.assertEqual(day_count.numerator, 366)
                
    def test_calc_days(self):
        days = self.day_count.calc_days(self.start_date, self.end_date)
        self.assertEqual(days, 364)
        
    def test_calc_days_leap_year(self):
        day_count = ACT_360(inception=pd.to_datetime('2019-06-01'), maturity=pd.to_datetime('2020-05-31'))
        days = day_count.calc_days(self.sf_leap, self.ed_leap)
        self.assertEqual(days, 274)
        
    def test_year_frac_ytm(self):
        year_frac = self.day_count.year_frac_ytm(self.start_date, self.end_date)
        self.assertAlmostEqual(year_frac, 0.997260, places=6)
        
    def test_year_frac_ytm_leap_year(self):
        day_count = ACT_360(inception=pd.to_datetime('2019-06-01'), maturity=pd.to_datetime('2020-05-31'))
        year_frac = day_count.year_frac_ytm(self.sf_leap, self.ed_leap)
        self.assertAlmostEqual(year_frac, 0.748634, places=6)
        
    def test_year_frac_price(self):
        year_frac = self.day_count.year_frac_price(self.start_date, self.end_date)
        self.assertAlmostEqual(year_frac, 1.011111, places=6)
        
    def test_year_frac_price_leap_year(self):
        day_count = ACT_360(inception=pd.to_datetime('2019-06-01'), maturity=pd.to_datetime('2020-05-31'))
        year_frac = day_count.year_frac_price(self.sf_leap, self.ed_leap)
        self.assertAlmostEqual(year_frac, 0.761111, places=6)
        
        
if __name__ == '__main__':
    unittest.main()
