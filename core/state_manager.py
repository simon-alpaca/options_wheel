from .utils import parse_option_symbol
from alpaca.trading.enums import AssetClass

def update_state(all_positions):    
    """
    Given the current positions, return a state dictionary describing where in the wheel each symbol is.
    """

    state = {}

    for p in all_positions:
        if p.asset_class == AssetClass.US_EQUITY:
            if int(p.qty) <= 0:
                raise ValueError(f"Only long stock positions allowed! Got {p.symbol} with qty {p.qty}")

            underlying = p.symbol
            if underlying in state:
                if state[underlying]["type"] != "short_call_awaiting_stock":
                    raise ValueError(f"Unexpected state for {underlying}: {state[underlying]}")
                state[underlying]["type"] = "short_call"
            else:
                state[underlying] = {"type": "long_shares", "price": float(p.avg_entry_price), "qty": int(p.qty)}

        elif p.asset_class == AssetClass.US_OPTION:
            if int(p.qty) >= 0:
                raise ValueError(f"Only short option positions allowed! Got {p.symbol} with qty {p.qty}")

            underlying, option_type = parse_option_symbol(p.symbol)

            if underlying in state:
                if not (state[underlying]["type"] == "long_shares" and option_type == 'C'):
                    raise ValueError(f"Unexpected state for {underlying}: {state[underlying]} with option {option_type}")
                state[underlying]["type"] = "short_call"
            else:
                if option_type == "C":
                    state[underlying] = {"type": "short_call_awaiting_stock", "price": None}
                elif option_type == "P":
                    state[underlying] = {"type": "short_put", "price": None}
                else:
                    raise ValueError(f"Unknown option type: {option_type}")

    # Final validation
    for underlying, st in state.items():
        if st["type"] not in {"short_put", "long_shares", "short_call"}:
            raise ValueError(f"Invalid final state for {underlying}: {st}")
        
    return state