from abc import ABC, abstractmethod


class Asset():
    
    def load_price_history(self, prices: pd.Series):
        self.prices = prices

    def update_price(self, prices: pd.Series):
        self.prices = prices.combine_first(self.prices)

