import pytest

import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal, assert_frame_equal

from ..classes import Asset, Debt


def test_Asset():
    asset = Asset()
    with pytest.raises(AssertionError):
        asset.load_price_history(pd.Series(1))
    with pytest.raises(AssertionError):
        asset.update_price(pd.Series(1))
    
    start_date = pd.Timestamp('2023-06-01')
    end_date = pd.Timestamp('2023-06-30')

    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    old_prices = np.random.rand(dates.shape[0])*6 + 97
    old_prices = pd.Series(data=old_prices, index=dates)

    asset.load_price_history(old_prices)
    assert_series_equal(asset.prices, old_prices)
    
    start_date = pd.Timestamp('2023-06-25')
    end_date = pd.Timestamp('2023-07-05')

    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    new_prices = np.random.rand(dates.shape[0])*6 + 97
    new_prices = pd.Series(data=new_prices, index=dates)

    asset.update_price(new_prices)
    old_dates = list(set(old_prices.index) - set(new_prices.index))
    
    assert_series_equal(asset.prices.loc[old_dates], old_prices[old_dates])
    assert_series_equal(asset.prices.loc[new_prices.index], new_prices)
    

def test_Debt():
    
    inception_date = '2022-01-01'
    debt = Debt(inception=inception_date)
    assert debt.inception == pd.Timestamp(inception_date)
    
    with pytest.raises(AssertionError):
        debt = Debt(inception='2022-01-01', maturity='2021-01-01')
        
    maturity_date = '2022-01-05'
    debt = Debt(inception=inception_date, maturity=maturity_date)
    assert debt.maturity == pd.Timestamp(maturity_date)
    
    rate = 0.05
    dates = [
        '2022-01-01',
        '2022-01-02',
        '2022-01-03',
        '2022-01-04',
        '2022-01-05'
    ]
    dates = pd.to_datetime(dates)
    rates = [rate, rate, rate, rate, rate]
    expected_rate_schedule = pd.Series(data=rates, index=dates)
    debt = Debt(rate=rate, maturity=maturity_date, inception=inception_date)
#     breakpoint()
    assert_series_equal(debt.rate, expected_rate_schedule, check_freq=False)
    
    rate1 = 0.04
    rate2 = 0.06
    rates = [rate1, rate1, rate2, rate2, rate2]
    input_rate_schedule = pd.Series(data=rates)
    with pytest.raises(AssertionError):
        debt = Debt(rate=input_rate_schedule, maturity=maturity_date, inception=inception_date)
    
    rate = 0.05
    dates = [
        '2021-01-01',  #older than inception
        '2022-01-02',
        '2022-01-03',
        '2022-01-04',
        '2022-01-05'
    ]
    dates = pd.to_datetime(dates)
    rates = [rate, rate, rate, rate, rate]
    with pytest.raises(AssertionError):
        debt = Debt(rate=input_rate_schedule, maturity=maturity_date, inception=inception_date)
    
    rate = 0.05
    dates = [
        '2022-01-01',
        '2022-01-02',
        '2022-01-03',
        '2022-01-04',
        '2023-01-05'  #later than maturity
    ]
    dates = pd.to_datetime(dates)
    rates = [rate, rate, rate, rate, rate]
    with pytest.raises(AssertionError):
        debt = Debt(rate=input_rate_schedule, maturity=maturity_date, inception=inception_date)
    
    dates = [
        '2022-01-01',
        '2022-01-02',
        '2022-01-03',
        '2022-01-04',
        '2022-01-05'
    ]
    dates = pd.to_datetime(dates)
    input_rate_schedule = pd.Series(data=rates, index=dates)
    assert_series_equal(debt.rate, input_rate_schedule, check_freq=False)
    
    input_pmt_schedule = pd.Series({
        '2022-01-02': 0.04,
        '2022-01-05': 1.04
    })
    with pytest.raises(AssertionError):
        debt = Debt(pmt_schedule=input_pmt_schedule, maturity=maturity_date, inception=inception_date)
        
    input_pmt_schedule = pd.Series({
        '2021-01-02': 0.04,  # older than inception
        '2022-01-05': 1.04
    })
    input_pmt_schedule.index = pd.to_datetime(input_pmt_schedule.index)
    with pytest.raises(AssertionError):
        debt = Debt(pmt_schedule=input_pmt_schedule, maturity=maturity_date, inception=inception_date)
        
    input_pmt_schedule = pd.Series({
        '2022-01-02': 0.04,
        '2023-01-05': 1.04  # later than maturity
    })
    input_pmt_schedule.index = pd.to_datetime(input_pmt_schedule.index)
    with pytest.raises(AssertionError):
        debt = Debt(pmt_schedule=input_pmt_schedule, maturity=maturity_date, inception=inception_date)   
        
    input_pmt_schedule = pd.DataFrame({
        '2022-01-02': [0.04, 0.5],
        '2022-01-05': [0.04, 0.5]
    }, index=['rate', 'fv']).T  # incorrect column names
    input_pmt_schedule.index = pd.to_datetime(input_pmt_schedule.index)
    with pytest.raises(AssertionError):
        debt = Debt(pmt_schedule=input_pmt_schedule, maturity=maturity_date, inception=inception_date)
        
    input_pmt_schedule = pd.DataFrame({
        '2022-01-02': [0.04, 0.5],
        '2022-01-05': [0.04, 0.5]
    }, index=['interest', 'principal']).T  # incorrect column names
    input_pmt_schedule.index = pd.to_datetime(input_pmt_schedule.index)
    debt = Debt(pmt_schedule=input_pmt_schedule, maturity=maturity_date, inception=inception_date)
    assert_frame_equal(debt.pmt_schedule, input_pmt_schedule, check_freq=False)
     
    