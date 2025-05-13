import argparse
from pathlib import Path
from core.broker_client import BrokerClient
from core.execution import sell_puts, sell_calls
from core.state_manager import update_state
from config.credentials import ALPACA_API_KEY, ALPACA_SECRET_KEY, IS_PAPER

SYMBOLS_FILE = Path(__file__).parent.parent / "config" / "symbol_list.txt"
with open(SYMBOLS_FILE, 'r') as file:
    SYMBOLS = [line.strip() for line in file.readlines()]

def main(fresh_start=False):
    client = BrokerClient(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, paper=IS_PAPER)

    if fresh_start:
        print("Running in fresh start mode — liquidating all positions.")
        client.liquidate_all_positions()

        allowed_symbols = SYMBOLS
    else:
        positions = client.get_positions()
        states = update_state(positions)

        for symbol, state in states.items():
            if state["type"] == "long_shares":
                sell_calls(client, symbol, state["price"], state["qty"])

        allowed_symbols = set(SYMBOLS).difference(states.keys())

    sell_puts(client, allowed_symbols)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-start", action="store_true", help="Liquidate all positions before running")
    args = parser.parse_args()

    main(fresh_start=args.fresh_start)
