import logging
from .strategy import filter_underlying, filter_options, score_options, select_options
from models.contract import Contract
import numpy as np

logger = logging.getLogger(f"strategy.{__name__}")

def sell_puts(client, allowed_symbols, buying_power, strat_logger = None):
    """
    Scan allowed symbols and sell short puts up to the buying power limit.
    """
    if not allowed_symbols or buying_power <= 0:
        return

    logger.info("Searching for put options...")
    filtered_symbols = filter_underlying(client, allowed_symbols, buying_power)
    strat_logger.set_filtered_symbols(filtered_symbols)
    if len(filtered_symbols) == 0:
        logger.info("No symbols found with sufficient buying power.")
        return
    option_contracts = client.get_options_contracts(filtered_symbols, 'put')
    snapshots = client.get_option_snapshot([c.symbol for c in option_contracts])
    put_options = filter_options([Contract.from_contract_snapshot(contract, snapshots.get(contract.symbol, None)) for contract in option_contracts if snapshots.get(contract.symbol, None)])
    if strat_logger:
        strat_logger.log_put_options([p.to_dict() for p in put_options])
    
    if put_options:
        logger.info("Scoring put options...")
        scores = score_options(put_options)
        put_options = select_options(put_options, scores)
        for p in put_options:
            buying_power -= 100 * p.strike 
            if buying_power < 0:
                break
            logger.info(f"Selling put: {p.symbol}")
            client.market_sell(p.symbol)
            if strat_logger:
                strat_logger.log_sold_puts([p.to_dict()])
    else:
        logger.info("No put options found with sufficient delta and open interest.")

def sell_calls(client, symbol, purchase_price, stock_qty, strat_logger = None):
    """
    Select and sell covered calls.
    """
    if stock_qty < 100:
        msg = f"Not enough shares of {symbol} to cover short calls!  Only {stock_qty} shares are held and at least 100 are needed!"
        logger.error(msg)
        raise ValueError(msg)

    logger.info(f"Searching for call options on {symbol}...")
    call_options = filter_options([Contract.from_contract(option, client) for option in client.get_options_contracts([symbol], 'call')], purchase_price)
    if strat_logger:
        strat_logger.log_call_options([c.to_dict() for c in call_options])

    if call_options:
        scores = score_options(call_options)
        contract = call_options[np.argmax(scores)]
        logger.info(f"Selling call option: {contract.symbol}")
        client.market_sell(contract.symbol)
        if strat_logger:
            strat_logger.log_sold_calls(contract.to_dict())
    else:
        logger.info(f"No viable call options found for {symbol}")