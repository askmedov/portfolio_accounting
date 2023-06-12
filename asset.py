import pandas as pd


DT_SERIES_ERROR = "pd.Series index must be pd.DateTimeIndex"


class Asset:
    
    prices = None
    updated_at = None
    asset_id = None

    
class AssetMethods():
    
    def __init__(self, asset: Asset):
        self.asset = asset
    
    def set_id(self, asset_id: str):
        self.asset.asset_id = asset_id
        self.asset.updated_at = pd.to_datetime('today')
        
    def set_price_history(self, prices: pd.Series):
        assert isinstance(prices.index, pd.DatetimeIndex), DT_SERIES_ERROR
        self.asset.prices = prices
        self.asset.updated_at = pd.to_datetime('today')

    def update_price(self, prices: pd.Series):
        assert isinstance(prices.index, pd.DatetimeIndex), DT_SERIES_ERROR
        self.asset.prices = prices.combine_first(self.asset.prices)
        self.asset.updated_at = pd.to_datetime('today')
