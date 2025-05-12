from core.broker_client import BrokerClient
from core.execution import fresh_start, sell_calls
from core.state_manager import update_state
from config.credentials import ALPACA_API_KEY, ALPACA_SECRET_KEY, IS_PAPER
from pathlib import Path

SYMBOLS_FILE = Path(__file__).parent.parent / "config" / "symbol_list.txt"
with open(SYMBOLS_FILE, 'r') as file:
    SYMBOLS = [line.strip() for line in file.readlines()]

def main():
    client = BrokerClient(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, paper=IS_PAPER)

    positions = client.get_positions()
    states = update_state(positions)

    for symbol, state in states.items():
        if state["type"] == "long_shares":
            sell_calls(client, symbol, state["price"], state["qty"])

    allowed_symbols = set(SYMBOLS).difference(states.keys())
    fresh_start(client, allowed_symbols)

if __name__ == "__main__":
    main()
