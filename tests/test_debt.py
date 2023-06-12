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
from asset import Asset, AssetMethods
from debt import Debt, DebtMethods


class DebtTests(unittest.TestCase):
    def setUp(self):
        self.debt = Debt()
        self.debt_methods = DebtMethods(self.debt)

    def test_set_attributes(self):
        # Test with valid inputs
        inception = datetime(2023, 1, 1)
        maturity = datetime(2023, 1, 5)
        rate = 0.05
        face_value = 1000
        pmt_schedule = pd.Series([100, 200, 300], index=pd.date_range(start=inception, periods=3, freq='D'))
        convention = DayCount.ACT_360

        self.debt_methods.set_attributes(
            inception=inception,
            maturity=maturity,
            rate=rate,
            face_value=face_value,
            pmt_schedule=pmt_schedule,
            convention=convention
        )

        self.assertEqual(self.debt.inception, inception)
        self.assertEqual(self.debt.maturity, maturity)
        expected_rates = pd.Series(data=np.ones(5) * rate, index=pd.date_range(start=inception, end=maturity, freq='D'))
        assert_series_equal(self.debt.rate, expected_rates, check_dtype=False)
        self.assertEqual(self.debt.face_value, face_value)
        assert_series_equal(self.debt.pmt_schedule, pmt_schedule)
        self.assertEqual(self.debt.convention, convention)

        # Test with invalid inputs
        with self.assertRaises(AssertionError):
            self.debt_methods.set_attributes(maturity=inception)  # maturity before inception

        with self.assertRaises(AssertionError):
            wrong_rate = pd.Series(data=[1, 2, 3], index=[datetime(2022, 1, 1), datetime(2023, 1, 1), datetime(2024, 1, 1)])
            self.debt_methods.set_attributes(rate=wrong_rate)  # rate series not within inception and maturity dates

        with self.assertRaises(AssertionError):
            self.debt_methods.set_attributes(face_value=0)  # negative face value

        with self.assertRaises(AssertionError):
            wrong_pmt_schedule = pd.DataFrame({'interest': [100, 200], 'principal': [300, 400]})
            self.debt_methods.set_attributes(pmt_schedule=wrong_pmt_schedule)  # pmt_schedule dataframe with incorrect columns


    def test_set_price_history(self):
        # Set up debt attributes first
        self.debt_methods.set_attributes(inception=datetime(2023, 1, 1), maturity=datetime(2024, 1, 1))

        # Test with valid price history
        prices = pd.Series([100, 101, 102], index=pd.date_range(start=self.debt.inception, periods=3, freq='D'))

        self.debt_methods.set_price_history(prices)

        assert_series_equal(self.debt.prices, prices, check_dtype=False)

        # Test with invalid price history
        with self.assertRaises(AssertionError):
            wrong_price = pd.Series([100, 101, 102], index=pd.date_range(start='2022-12-31', periods=3, freq='D'))
            self.debt_methods.set_price_history(wrong_price)  # prices

            
if __name__ == "__main__":
    unittest.main()
