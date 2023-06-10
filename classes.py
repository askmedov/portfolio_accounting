from abc import ABC, abstractmethod


class Asset(ABC):
    
    @abstractmethod
    def load_price_history(prices: pd.Series):
        pass
    
    @abstractmethod
    def update_price(prices: pd.Series):
        pass

