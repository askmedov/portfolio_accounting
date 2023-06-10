import pytest
import pandas as pd
import numpy as np
from ..classes import Asset


def test_Asset():
    asset = Asset()
    with pytest.raises(AssertionError):
        asset.load_price_history(1)
    with pytest.raises(AssertionError):
        asset.load_price_history(pd.Series(1))
    with pytest.raises(AssertionError):
        asset.update_price(1)
    with pytest.raises(AssertionError):
        asset.update_price(pd.Series(1))
    
    start_date = pd.Timestamp('2023-06-01')
    end_date = pd.Timestamp('2023-06-30')

    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    old_prices = np.random.rand(dates.shape[0])*6 + 97
    old_prices = pd.Series(data=old_prices, index=dates)

    asset.load_price_history(old_prices)
    assert all(old_prices == asset.prices)
    
    start_date = pd.Timestamp('2023-06-25')
    end_date = pd.Timestamp('2023-07-05')

    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    new_prices = np.random.rand(dates.shape[0])*6 + 97
    new_prices = pd.Series(data=new_prices, index=dates)

    asset.update_price(new_prices)
    old_dates = list(set(old_prices.index) - set(new_prices.index))
    
    assert all(asset.prices.loc[old_dates] == old_prices[old_dates])
    assert all(asset.prices.loc[new_prices.index] == new_prices)
    
