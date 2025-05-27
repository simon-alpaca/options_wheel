# The max dollar risk allowed by the strategy.  
MAX_RISK = 80_000

# The range of allowed Delta (absolute value) when choosing puts or calls to sell.  
# The goal is to balance low assignment risk (lower Delta) with high premiums (higher Delta).
DELTA_MIN = 0.15 
DELTA_MAX = 0.30

# The range of allowed yield when choosing puts or calls to sell.
YIELD_MIN = 0.04
YIELD_MAX = 1.00

# The range of allowed days till expiry when choosing puts or calls to sell.
# The goal is to balance shorter expiry for consistent income generation with longer expiry for time value premium.
EXPIRATION_MIN = 0
EXPIRATION_MAX = 21

# Only trade contracts with at least this much open interest.
OPEN_INTEREST_MIN = 100

# The minimum score passed to core.strategy.select_options().
SCORE_MIN = 0.05