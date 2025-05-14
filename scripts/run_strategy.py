from pathlib import Path
from core.broker_client import BrokerClient
from core.execution import sell_puts, sell_calls
from core.state_manager import update_state, calculate_risk
from config.credentials import ALPACA_API_KEY, ALPACA_SECRET_KEY, IS_PAPER
from config.params import MAX_RISK
from logging.strategy_logger import StrategyLogger
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-start", action="store_true", help="Liquidate all positions before running")
    parser.add_argument("--log", action="store_true", help="Enable logging for the strategy run")
    args = parser.parse_args()

    logger = StrategyLogger(enabled=args.log)
    logger.set_fresh_start(args.fresh_start)

    SYMBOLS_FILE = Path(__file__).parent.parent / "config" / "symbol_list.txt"
    with open(SYMBOLS_FILE, 'r') as file:
        SYMBOLS = [line.strip() for line in file.readlines()]

    client = BrokerClient(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, paper=IS_PAPER)

    if args.fresh_start:
        print("Running in fresh start mode — liquidating all positions.")
        client.liquidate_all_positions()
        allowed_symbols = SYMBOLS
        buying_power = MAX_RISK
    else:
        positions = client.get_positions()
        logger.add_current_positions(positions)

        current_risk = calculate_risk(positions)
        
        states = update_state(positions)
        logger.add_state_dict(states)

        for symbol, state in states.items():
            if state["type"] == "long_shares":
                sell_calls(client, symbol, state["price"], state["qty"], logger)

        allowed_symbols = list(set(SYMBOLS).difference(states.keys()))
        buying_power = MAX_RISK - current_risk
    
    logger.set_buying_power(buying_power)
    logger.set_allowed_symbols(allowed_symbols)

    print(f"Current buying power is ${buying_power}")
    sell_puts(client, allowed_symbols, buying_power, logger)

    logger.save()    

if __name__ == "__main__":
    main()
