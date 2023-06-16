import os
import sys
import unittest
from datetime import datetime

import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal
from pyxirr import DayCount

package_path = '\\'.join(os.path.realpath(__file__).split('\\')[:-2])
sys.path.append(package_path)
from bill import Bill, BillMethods


class TestBillMethods(unittest.TestCase):

    def setUp(self):
        self.bill = Bill()
        self.bill_methods = BillMethods(self.bill)

    def test_set_attributes(self):
        isin = 'ABC123'
        inception = datetime(2022, 6, 29)
        maturity = datetime(2023, 6, 29)
        face_value = 1000
        pmt_schedule = pd.Series({maturity: face_value})
        self.bill_methods.set_attributes(isin=isin, maturity=maturity, face_value=face_value, inception=inception)
        assert_series_equal(self.bill.pmt_schedule, pmt_schedule)

    def test_calc_ytm(self):
        self.bill.maturity = datetime(2023, 6, 29)
        self.bill.prices = pd.Series([90, 91, 92, 93, 94], index=pd.date_range(start='2023-01-01', periods=5))
        ytm = self.bill_methods.calc_ytm(return_series=True)
        expected_ytm = pd.Series([22.656735, 20.280282, 17.931712, 15.6097265, 13.313070], name='ytm',\
                                      index=pd.date_range(start='2023-01-01', periods=5))
        expected_ytm = expected_ytm/100
        assert_series_equal(ytm, expected_ytm)

    def test_calc_discount(self):
        self.bill.maturity = datetime(2023, 6, 29)
        self.bill.prices = pd.Series([90, 91, 92, 93, 94], index=pd.date_range(start='2023-01-01', periods=5))
        discount = self.bill_methods.calc_discount(return_series=True)
        expected_discount = pd.Series([20.111732, 18.202247, 16.271186, 14.318182, 12.342857], name='discount',\
                                      index=pd.date_range(start='2023-01-01', periods=5))
        assert_series_equal(discount, expected_discount)

    def test_calc_price(self):
        self.bill.maturity = datetime(2023, 6, 29)
        discounts = pd.Series([5, 6, 7, 8, 9], name='discount', index=pd.date_range(start='2023-01-01', periods=5))
        prices = self.bill_methods.calc_price(discounts)
        expected_prices = pd.Series([97.513889, 97.033333, 96.558333, 96.088889, 95.625000], name='price',\
                                      index=pd.date_range(start='2023-01-01', periods=5))
        assert_series_equal(prices, expected_prices)

    def test_set_price_history(self):
        self.bill.maturity = datetime(2023, 6, 29)
        discounts = pd.Series([5, 6, 7, 8, 9], name='discount', index=pd.date_range(start='2023-01-01', periods=5))
        expected_prices = pd.Series([97.513889, 97.033333, 96.558333, 96.088889, 95.625000], name='price',\
                                      index=pd.date_range(start='2023-01-01', periods=5))
        self.bill_methods.set_price_history(discounts)
        assert_series_equal(self.bill.prices, expected_prices)

    def test_update_price(self):
        self.bill.maturity = datetime(2023, 6, 29)
        discounts_old = pd.Series([5, 6, 7, 8, 9], name='discount', index=pd.date_range(start='2023-01-01', periods=5))
        self.bill_methods.set_price_history(discounts_old)
        
        discounts_new = pd.Series([10, 11], name='discount', index=pd.date_range(start='2023-01-04', periods=2))
        self.bill_methods.update_price(discounts_new)
        
        expected_prices = pd.Series([97.513889, 97.033333, 96.558333, 95.111111 , 94.652778], name='price',\
                                      index=pd.date_range(start='2023-01-01', periods=5))
        assert_series_equal(self.bill.prices, expected_prices)


if __name__ == '__main__':
    unittest.main()
