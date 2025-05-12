from typing import Optional
from dataclasses import dataclass, field
import datetime
from core.broker_client import BrokerClient

@dataclass
class Contract:
    underlying: str
    symbol: str
    contract_type: str

    dte: Optional[float] = None  # Days to expiration
    strike: Optional[float] = None
    delta: Optional[float] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    last_price: Optional[float] = None
    oi: Optional[int] = None  # Open interest
    underlying_price: Optional[float] = None
    client: Optional["BrokerClient"] = field(default=None, repr=False, compare=False)


    def __post_init__(self):
        if self.client:
            self.update()

    @classmethod
    def from_contract(cls, contract, client=None) -> "Contract":
        """
        Create a StandardizedOptionContract from a raw OptionsContract.
        """
        return cls(
            underlying = contract.underlying_symbol,
            symbol = contract.symbol,
            contract_type = contract.type.title().lower(),
            oi = float(contract.open_interest) if contract.open_interest is not None else None,
            dte = (contract.expiration_date - datetime.date.today()).days,
            strike = contract.strike_price,
            client = client
        )
    
    def update(self):
        """
        Fetches and updates the contract's bid, ask, delta, and other market data.
        Requires a valid client to interact with the API.
        """
        if not self.client:
            raise ValueError("Cannot update Contract without a client.")
        
        snapshot = self.client.get_option_snapshot(self.symbol)
        if snapshot and self.symbol in snapshot:
            data = snapshot[self.symbol]
            if hasattr(data, 'greeks') and data.greeks:
                self.delta = data.greeks.delta
            if hasattr(data, 'latest_quote') and data.latest_quote:
                self.bid_price = data.latest_quote.bid_price
                self.ask_price = data.latest_quote.ask_price
                self.last_price = getattr(data.latest_trade, "price", None)
            if hasattr(data, 'latest_trade') and data.latest_trade:
                self.last_price = data.latest_trade.price
        
        # underlying_latest_trade = get_stock_latest_trade(self.underlying)
        # if underlying_latest_trade and self.underlying in underlying_latest_trade:
        #     data = underlying_latest_trade[self.underlying]
        #     if hasattr(data, 'price'):
        #         self.underlying_price = data.price
