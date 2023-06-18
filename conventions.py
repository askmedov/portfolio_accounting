from abc import ABC, abstractmethod

import pandas as pd


class DayCount(ABC):
    
    numerator = None
    denominator = None
    
    @abstractmethod
    def calc_days(self):
        pass
    
    @abstractmethod
    def year_frac_ytm(self):
        pass
    
    @abstractmethod
    def year_frac_price(self):
        pass
    
    
class ACT_360(DayCount):
    
    def __init__(self, inception=None, maturity=None):
        if inception is None and maturity is None:
            self.numerator = 365
        elif (maturity - inception).days == 366 and \
             (inception + pd.DateOffset(years=1) == maturity):
            # Debt with maturity of exactly 1-year and there are 366 days in the next 12 months 
            self.numerator = 366
        elif (maturity - inception).days <= 365 and \
             ((inception + pd.DateOffset(years=1) - inception).days == 366):
            # Debt with maturity of 1-year or less, where there are 366 days in the next 12 months 
            self.numerator = 366
        else:
            # Only T-Bill behavior is implemented as of right now 
            self.numerator = 365
        
        self.denominator = 360
        
    def calc_days(self, start_date, end_date):
        return (end_date - start_date).days
    
    def year_frac_ytm(self, start_date, end_date):
        return (end_date - start_date).days/self.numerator
    
    def year_frac_price(self, start_date, end_date):
        return (end_date - start_date).days/self.denominator
        