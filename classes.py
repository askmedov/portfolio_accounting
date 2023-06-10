from functools import partial
from typing import Union

import numpy as np
import pandas as pd
from pyxirr import DayCount, xirr


DT_SERIES_ERROR = "pd.Series index must be pd.DateTimeIndex"


def _ytm(row, convention):
    _amounts = row.values
    _dates = row.index[1:].insert(0, row.name)
    return xirr(_dates, _amounts, day_count=convention)


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
                 pmt_schedule: Union[pd.Series, pd.DataFrame] = None,
                 convention: DayCount = DayCount.THIRTY_360_ISDA):
        
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
        
        assert isinstance(convention, DayCount)
        self.convention = convention
        
    def load_price_history(self, prices: pd.Series):
        if self.inception is not None:
            assert prices.index.min() >= self.inception, "prices start before inception" 
        if self.maturity is not None:
            assert prices.index.max() <= self.maturity, "prices end after maturity"
        super().load_price_history(prices)
   
    def update_price(self, prices: pd.Series):
        if self.inception is not None:
            assert prices.index.min() >= self.inception, "prices start before inception"
        if self.maturity is not None:
            assert prices.index.max() <= self.maturity, "prices end after maturity"
        super().update_price(prices)


class Bill(Debt):
    
    def __init__(self, 
                 inception: Union[pd.Timestamp, str] = 'today',
                 maturity: Union[pd.Timestamp, str] = None,
                 face_value: Union[int, float] = 1,
                 convention: DayCount = DayCount.ACT_360):
        
        pmt_schedule = pd.Series({pd.to_datetime(maturity): face_value})
        
        super().__init__(inception=inception, 
                         maturity=maturity, 
                         face_value=face_value, 
                         pmt_schedule=pmt_schedule, 
                         convention=convention)
        
    def calc_ytm(self, return_series=False):
        
        assert hasattr(self, 'prices') and self.prices is not None
        amounts = self.prices.to_frame(name='price')
        amounts['price'] = amounts['price']*-1
        for date, pmt in self.pmt_schedule.iteritems():
            amounts[date] = pmt

        for col in amounts.columns:
            if col == 'price':
                continue
            amounts[col] = np.where(amounts.index <= col, amounts[col], 0)
        
        ytm_func = partial(_ytm, convention=self.convention)
        self.ytm = amounts.apply(ytm_func, axis=1)
        if return_series:
            return self.ytm
        
