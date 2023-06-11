import os
import sys
import unittest

import pandas as pd
from pandas.testing import assert_series_equal

package_path = '\\'.join(os.path.realpath(__file__).split('\\')[:-2])
sys.path.append(package_path)
from asset import Asset, AssetMethods


DT_SERIES_ERROR = "prices should be a pandas Series with a DatetimeIndex"


class AssetMethodsTest(unittest.TestCase):
    def setUp(self):
        self.asset = Asset()
        self.asset_methods = AssetMethods(self.asset)

    def test_set_id(self):
        self.asset_methods.set_id("12345")
        self.assertEqual(self.asset.asset_id, "12345")

    def test_set_price_history(self):
        prices = pd.Series([10, 20, 30], index=pd.date_range('2022-01-01', periods=3))
        self.asset_methods.set_price_history(prices)
        assert_series_equal(self.asset.prices, prices)

    def test_update_price(self):
        old_prices = pd.Series([10, 20, 30], index=pd.date_range('2022-01-01', periods=3))
        new_prices = pd.Series([40, 50, 60], index=pd.date_range('2022-01-03', periods=3))
        expected_prices = pd.Series([10, 20, 40, 50, 60], index=pd.date_range('2022-01-01', periods=5))
        self.asset_methods.set_price_history(old_prices)
        self.asset_methods.update_price(new_prices)
        assert_series_equal(self.asset.prices, expected_prices, check_dtype=False)

    def test_set_price_history_invalid(self):
        prices = pd.Series([10, 20, 30], index=[1, 2, 3])  # Non-DatetimeIndex
        with self.assertRaises(AssertionError):
            self.asset_methods.set_price_history(prices)

    def test_update_price_invalid(self):
        old_prices = pd.Series([10, 20, 30], index=pd.date_range('2022-01-01', periods=3))
        new_prices = pd.Series([40, 50, 60], index=[1, 2, 3])  # Non-DatetimeIndex
        self.asset.prices = old_prices
        with self.assertRaises(AssertionError):
            self.asset_methods.update_price(new_prices)

if __name__ == "__main__":
    unittest.main()
    
