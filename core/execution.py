from .strategy import *
from models.contract import Contract
import numpy as np

def sell_puts(client, allowed_symbols, buying_power):
    """
    Scan allowed symbols and sell short puts up to the buying power limit.
    """
    if not allowed_symbols or buying_power <= 0:
        return

    print("Searching for put options...")
    filtered_symbols = filter_underlying(client, allowed_symbols, buying_power)
    if len(filtered_symbols) == 0:
        print("No symbols found with sufficient buying power.")
        return
    option_contracts = client.get_options_contracts(filtered_symbols, 'put')
    snapshots = client.get_option_snapshot([c.symbol for c in option_contracts])
    put_options = filter_options([Contract.from_contract_snapshot(contract, snapshots.get(contract.symbol, None)) for contract in option_contracts])
    
    if put_options:
        print("Scoring put options...")
        scores = score_options(put_options)
        put_options = select_options(put_options, scores)
        for p in put_options:
            buying_power -= 100 * p.strike 
            if buying_power < 0:
                break
            print(f"Selling put: {p.symbol}")
            client.market_sell(p.symbol)
    else:
        print("No put options found with sufficient delta and open interest.")

def sell_calls(client, symbol, purchase_price, stock_qty):
    """
    Select and sell covered calls.
    """
    if stock_qty < 100:
        raise ValueError(f"Not enough shares of {symbol} to cover short calls!  Only {stock_qty} shares are held and at least 100 are needed!")

    print(f"Searching for call options on {symbol}...")
    call_options = filter_options([Contract.from_contract(option, client) for option in client.get_options_contracts([symbol], 'call')], purchase_price)
    
    if call_options:
        scores = score_options(call_options)
        contract = call_options[np.argmax(scores)]
        print(f"Selling call option: {contract.symbol}")
        client.market_sell(contract.symbol)