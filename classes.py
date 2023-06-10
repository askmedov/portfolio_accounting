from typing import Union

import numpy as np
import pandas as pd


DT_SERIES_ERROR = "pd.Series index must be pd.DateTimeIndex"


class Asset():
    
    def load_price_history(self, prices: pd.Series):
        assert isinstance(prices.index, pd.DatetimeIndex), DT_SERIES_ERROR
        self.prices = prices

    def update_price(self, prices: pd.Series):
        assert isinstance(prices.index, pd.DatetimeIndex), DT_SERIES_ERROR
        self.prices = prices.combine_first(self.prices)

        
class Debt(Asset):
    
    def __init__(self, 
                 inception: Union[pd.Timestamp, str] = 'today',
                 maturity: Union[pd.Timestamp, str] = None,
                 rate: Union[float, pd.Series] = None,
                 face_value: Union[int, float] = 1,
                 pmt_schedule: Union[pd.Series, pd.DataFrame] = None):
        
        if isinstance(inception, str):
            inception = pd.to_datetime(inception)
        self.inception = inception
        
        if isinstance(maturity, str):
            maturity = pd.to_datetime(maturity)
        
        if maturity is not None:
            assert maturity >= self.inception, "Maturity date is before inception date!"
        self.maturity = maturity    
        
        if isinstance(rate, float) and maturity is not None:
            dates = pd.date_range(start=self.inception, end=self.maturity, freq='D')
            rates = np.ones(dates.shape[0]) * rate
            self.rate = pd.Series(data=rates, index=dates)
        elif isinstance(rate, pd.Series):
            assert isinstance(rate.index, pd.DatetimeIndex), DT_SERIES_ERROR
            assert rate.index.min() >= self.inception
            assert rate.index.max() <= self.maturity
            self.rate = rate
            
        self.face_value = face_value
        
        if type(pmt_schedule) in (pd.Series, pd.DataFrame):
            assert isinstance(pmt_schedule.index, pd.DatetimeIndex), DT_SERIES_ERROR
            assert pmt_schedule.index.min() >= self.inception
            assert pmt_schedule.index.max() <= self.maturity
        if isinstance(pmt_schedule, pd.DataFrame):
            err_msg = "columns of payment schedule must be ['interest', 'principal']"
            assert all(pmt_schedule.columns == ['interest', 'principal']), err_msg
        self.pmt_schedule = pmt_schedule
        
