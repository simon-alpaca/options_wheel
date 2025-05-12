import re

def parse_option_symbol(symbol):
    """
    Extracts the underlying symbol and option type ('P' or 'C') from an option symbol.
    
    Example:
        'AAPL250516P00207500' -> ('AAPL', 'P')
    """
    match = re.match(r'^([A-Za-z]+)(\d{6})([PC])(\d+)$', symbol)
    
    if match:
        underlying = match.group(1)
        option_type = match.group(3)
        return underlying, option_type
    else:
        raise ValueError(f"Invalid option symbol format: {symbol}")