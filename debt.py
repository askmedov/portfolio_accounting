from typing import Union
import datetime

import numpy as np
import pandas as pd

from asset import Asset, AssetMethods
from constants import DT_SERIES_ERROR
from conventions import DayCount, ACT_360


class Debt(Asset):
    
    inception = None
    maturity = None
    rate = None
    face_value = None
    pmt_schedule = None
    convention = None

    
class DebtMethods(AssetMethods):
    
    def __init__(self, debt: Debt):
        self.debt = debt
        super().__init__(self.debt)
        
    def set_attributes(self, 
                 inception: Union[pd.Timestamp, str, datetime.date, datetime.datetime] = 'today',
                 maturity: Union[pd.Timestamp, str, datetime.date, datetime.datetime] = None,
                 rate: Union[float, pd.Series] = None,
                 face_value: Union[int, float] = 1,
                 pmt_schedule: Union[pd.Series, pd.DataFrame] = None,
                 convention: DayCount = ACT_360):
        
        if isinstance(inception, str):
            inception = pd.to_datetime(inception)
        self.debt.inception = inception
        
        if isinstance(maturity, str):
            maturity = pd.to_datetime(maturity)
        if maturity is not None:
            assert maturity >= self.debt.inception, "Maturity date is before inception date!"
        self.debt.maturity = maturity    
        
        if isinstance(rate, float) and maturity is not None:
            dates = pd.date_range(start=self.debt.inception, end=self.debt.maturity, freq='D')
            rates = np.ones(dates.shape[0]) * rate
            self.debt.rate = pd.Series(data=rates, index=dates)
        elif isinstance(rate, pd.Series):
            assert isinstance(rate.index, pd.DatetimeIndex), DT_SERIES_ERROR
            assert rate.index.min() >= self.debt.inception
            assert rate.index.max() <= self.debt.maturity
            self.debt.rate = rate
        
        assert face_value > 0, "Face value cannot be 0 or negative!"
        self.debt.face_value = face_value
        
        if type(pmt_schedule) in (pd.Series, pd.DataFrame):
            assert isinstance(pmt_schedule.index, pd.DatetimeIndex), DT_SERIES_ERROR
            assert pmt_schedule.index.min() >= self.debt.inception
            assert pmt_schedule.index.max() <= self.debt.maturity
        if isinstance(pmt_schedule, pd.DataFrame):
            err_msg = "columns of payment schedule must be ['interest', 'principal']"
            assert all(pmt_schedule.columns == ['interest', 'principal']), err_msg
        self.debt.pmt_schedule = pmt_schedule
        
        self.debt.convention = convention(inception=self.debt.inception,
                                          maturity=self.debt.maturity)
        
    def set_price_history(self, prices: pd.Series):
        if self.debt.inception is not None:
            assert prices.index.min() >= self.debt.inception, "prices start before inception" 
        if self.debt.maturity is not None:
            assert prices.index.max() <= self.debt.maturity, "prices end after maturity"
        super().set_price_history(prices)
   
    def update_price(self, prices: pd.Series):
        if self.debt.inception is not None:
            assert prices.index.min() >= self.debt.inception, "prices start before inception"
        if self.debt.maturity is not None:
            assert prices.index.max() <= self.debt.maturity, "prices end after maturity"
        super().update_price(prices)