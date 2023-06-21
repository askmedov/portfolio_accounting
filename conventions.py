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
        
        self.inception = inception
        self.maturity = maturity
        
        self.denominator = 360
        
    def numerator(self, start_date=None, end_date=None):
        if (self.inception is None) or \
           (self.inception is not None and self.maturity is None) or \
           (self.inception is not None and self.maturity is not None and (self.maturity - self.inception).days > 366): 
            
            tot_years = int((end_date - start_date).days / 365)
            if tot_years == 0:
                if (start_date + pd.DateOffset(years=1) - start_date).days == 366:
                    return 366
                else:
                    return 365
            else:
                later_date = start_date + pd.DateOffset(years=tot_years)
                leap_years = (later_date - start_date).days % 365
                return 365 + leap_years/tot_years
        else:
            if (self.maturity - self.inception).days == 366 and \
                 (self.inception + pd.DateOffset(years=1) == self.maturity):
                # Debt with maturity of exactly 1-year and there are 366 days in the next 12 months 
                return 366
            elif (self.maturity - self.inception).days <= 365 and \
                 ((self.inception + pd.DateOffset(years=1) - self.inception).days == 366):
                # Debt with maturity of 1-year or less, where there are 366 days in the next 12 months 
                return 366
            else:
                return 365
        
    def calc_days(self, start_date, end_date):
        return (end_date - start_date).days
    
    def year_frac_ytm(self, start_date, end_date):
        return (end_date - start_date).days/self.numerator(start_date, end_date)
    
    def year_frac_price(self, start_date, end_date):
        return (end_date - start_date).days/self.denominator
        