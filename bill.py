from functools import partial
from typing import Union

import numpy as np
import pandas as pd
from pyxirr import DayCount

from debt import Debt, DebtMethods
from constants import DT_SERIES_ERROR


class Bill(Debt):
    
    isin = None
    discounts = None
    min_piece = None
    increment = None
    historic_ytm = None
    

class BillMethods(DebtMethods):
    
    def __init__(self, bill: Bill):
        self.bill = bill
        super().__init__(self.bill)
        
    def set_attributes(self, isin: str, min_piece: int = 100, increment: int = 100, **kwargs):
        
        self.bill.isin = isin
        self.bill.min_piece = min_piece
        self.bill.increment = increment
        
        if 'maturity' in kwargs and ('pmt_schedule' not in kwargs):
            pmt_schedule = pd.Series({pd.to_datetime(kwargs['maturity']): kwargs['face_value']})
            kwargs['pmt_schedule'] = pmt_schedule
        
        super().set_attributes(**kwargs)
    
    def calc_ytm(self, return_series=False):
        
        assert self.bill.prices is not None
        df = self.bill.prices.to_frame(name='price')
        
        df['date'] = df.index
        df['tenor'] = (self.bill.maturity - df['date']).dt.days / 365
        df['ytm'] = (100 / df['price'] - 1) / df['tenor']
        
        self.bill.historic_ytm = df['ytm']
        if return_series:
            return self.bill.historic_ytm
        
    def calc_discount(self, return_series=False, precision=6):
        assert self.bill.prices is not None
        df = self.bill.prices.to_frame(name='price')
        df['date'] = df.index
        df['tenor'] = (self.bill.maturity - df['date']).dt.days / 360
        df['discount'] = np.round((100 - df['price']) / df['tenor'], precision)
        
        self.bill.discounts = df['discount']
        if return_series:
            return self.bill.discounts
        
    def calc_price(self, discounts, precision=6):
        
        df = discounts.to_frame(name='discount')
        
        df['date'] = df.index
        df['tenor'] = (self.bill.maturity - df['date']).dt.days / 360
        df['price'] = 100 - np.round(df['discount'] * df['tenor'], precision)
        
        return df['price']
    
    def set_price_history(self, discounts: pd.Series):
        assert isinstance(discounts.index, pd.DatetimeIndex), DT_SERIES_ERROR
        prices = self.calc_price(discounts)
        super().set_price_history(prices)
        
    def update_price(self, discounts: pd.Series):
        assert isinstance(discounts.index, pd.DatetimeIndex), DT_SERIES_ERROR
        prices = self.calc_price(discounts)
        super().update_price(prices)
        
