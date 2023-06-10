import pandas as pd

class Asset():
    
    def load_price_history(self, prices: pd.Series):
        assert isinstance(prices, pd.Series), "Must provide pd.Series"
        assert isinstance(prices.index, pd.DatetimeIndex), "pd.Series index must be pd.DateTimeIndex"
        self.prices = prices

    def update_price(self, prices: pd.Series):
        assert isinstance(prices, pd.Series), "Must provide pd.Series"
        assert isinstance(prices.index, pd.DatetimeIndex), "pd.Series index must be pd.DateTimeIndex"
        self.prices = prices.combine_first(self.prices)
