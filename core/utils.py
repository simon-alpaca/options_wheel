import re

def parse_option_symbol(symbol):
    """
    Parses OCC-style option symbol.

    Example:
        'AAPL250516P00207500' -> ('AAPL', 'P', 207.5)
    """
    match = re.match(r'^([A-Za-z]+)(\d{6})([PC])(\d{8})$', symbol)
    
    if match:
        underlying = match.group(1)
        option_type = match.group(3)
        strike_raw = match.group(4)
        strike_price = int(strike_raw) / 1000.0
        return underlying, option_type, strike_price
    else:
        raise ValueError(f"Invalid option symbol format: {symbol}")
