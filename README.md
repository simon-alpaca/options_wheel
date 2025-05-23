# Automated Wheel Strategy
 
Welcome to the Wheel Strategy automation project!
This script is designed to help you trade the classic ["wheel" options strategy](https://alpaca.markets/learn/options-wheel-strategy) with as little manual work as possible.

---

## Strategy Logic

Here's the basic idea:

1. **Sell cash-secured puts** on stocks you wouldn't mind owning.
2. If you **get assigned**, buy the stock.
3. Then **sell covered calls** on the stock you own.
4. Keep collecting premiums until the stock gets called away.
5. Repeat the cycle!

This code helps pick the right puts and calls to sell, tracks your positions, and automatically turns the wheel to the next step.

---

## How to Run the Code

1. **Clone the repository:**

   ```bash
   git clone https://github.com/simon-alpaca/options_wheel.git
   cd options_wheel
   ```

2. **Create a virtual environment using [`uv`](https://github.com/astral-sh/uv):**

   ```bash
   uv venv
   source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
   ```

3. **Install the required packages:**

   ```bash
   uv pip install -e .
   ```

4. **Set up your API credentials:**

   Create a `.env` file in the project root with the following content:

   ```env
   ALPACA_API_KEY=your_public_key
   ALPACA_SECRET_KEY=your_private_key
   IS_PAPER=true  # Set to false if using a live account
   ```

   Your credentials will be loaded from `.env` automatically.

5. **Choose your symbols:**

   The strategy trades only the symbols listed in `config/symbol_list.txt`. Edit this file to include the tickers you want to run the Wheel strategy on — one symbol per line. Choose stocks you'd be comfortable holding long-term.

6. **Configure trading parameters:**

   Adjust values in `config/params.py` to customize things like buying power limits, options characteristics (e.g., greeks / expiry), and scoring thresholds. Each parameter is documented in the file.


7. **Run the strategy**

   Run the strategy (which assumes an empty or fully managed portfolio):
   
   ```bash
   run-strategy
   ```
   
   > **Tip:** On your first run, use `--fresh-start` to liquidate all existing positions and start clean.
   
   There are two types of logging:
   
   * **Strategy JSON logging** (`--strat-log`):
     Always saves detailed JSON files to disk for analyzing strategy performance.
   
   * **Runtime logging** (`--log-level` and `--log-to-file`):
     Controls console/file logs for monitoring the current run. Optional and configurable.
   
   **Flags:**
   
   * `--fresh-start` — Liquidate all positions before running (recommended first run).
   * `--strat-log` — Enable strategy JSON logging (always saved to disk).
   * `--log-level LEVEL` — Set runtime logging verbosity (default: INFO).
   * `--log-to-file` — Save runtime logs to file instead of console.
   
   Example:
   
   ```bash
   run-strategy --fresh-start --strat-log --log-level DEBUG --log-to-file
   ```
   
   For more info:
   
   ```bash
   run-strategy --help
   ```

---

### What the Script Does

* Checks your current positions to identify any assignments and sells covered calls on those.
* Filters your chosen stocks based on buying power (you must be able to afford 100 shares per put).
* Scores put options using `core.strategy.score_options()`, which ranks by annualized return discounted by the probability of assignment.
* Places trades for the top-ranked options.

---

### Notes

* **Account state matters**: This strategy assumes full control of the account — all positions are expected to be managed by this script. For best results, start with a clean account (e.g. by using the `--fresh-start` flag).
* **One contract per symbol**: To simplify risk management, this implementation trades only one contract at a time per symbol. You can modify this logic in `core/strategy.py` to suit more advanced use cases.
* The **user agent** for API calls defaults to `OPTIONS-WHEEL` to help Alpaca track usage of runnable algos and improve user experience.  You can opt out by adjusting the `USER_AGENT` variable in `core/user_agent_mixin.py` — though we kindly hope you’ll keep it enabled to support ongoing improvements.  
* **Want to customize the strategy?** The `core/strategy.py` module is a great place to start exploring and modifying the logic.

---

## Automating the Wheel

Running the script once will only turn the wheel a single time. To keep it running as a long-term income strategy, you'll want to automate it to run several times per day. This can be done with a cron job on Mac or Linux.

### Setting Up a Cron Job (Mac / Linux)

1. **Find the full path to the `run-strategy` command** by running:

   ```bash
   which run-strategy
   ```

   This will output something like:

   ```bash
   /Users/yourname/.local/share/virtualenvs/options_wheel-abc123/bin/run-strategy
   ```

2. **Open your crontab** for editing:

   ```bash
   crontab -e
   ```

3. **Add the following lines to run the strategy at 10:00 AM, 1:00 PM, and 3:30 PM on weekdays:**

   ```cron
   0 10 * * 1-5 /full/path/to/run-strategy >> /path/to/logs/run_strategy_10am.log 2>&1
   0 13 * * 1-5 /full/path/to/run-strategy >> /path/to/logs/run_strategy_1pm.log 2>&1
   30 15 * * 1-5 /full/path/to/run-strategy >> /path/to/logs/run_strategy_330pm.log 2>&1
   ```

   Replace `/full/path/to/run-strategy` with the output from the `which run-strategy` command above. Also replace `/path/to/logs/` with the directory where you'd like to store log files (create it if needed).

---

## Test Results

Some early backtests:

| Metric                            | Result |
| :-------------------------------- | :----- |
| Annualized Return                 | +XX%   |
| Win Rate                          | XX%    |
| Average Premium Collected (Puts)  | \$XXX  |
| Average Premium Collected (Calls) | \$XXX  |
| Max Drawdown                      | -XX%   |

> (Real trading results will vary depending on fills, slippage, assignment rates, etc.)

---

## Core Strategy Logic

The core logic is defined in `core/strategy.py`.

* **Stock Filtering:**
  The strategy filters underlying stocks based on available buying power. It fetches the latest trade prices for each candidate symbol and retains only those where the cost to buy 100 shares (`price × 100`) is within your buying power limit. This keeps trades within capital constraints and can be extended to include custom filters like volatility or technical indicators.

* **Option Filtering:**
  Put options are filtered by absolute delta, which must lie between `DELTA_MIN` and `DELTA_MAX`, and by open interest (`OPEN_INTEREST_MIN`) to ensure liquidity. For short calls, the strategy applies a minimum strike price filter (`min_strike`) to ensure the strike is above the underlying purchase price. This helps avoid immediate assignment and guarantees profit if the call is assigned.

* **Option Scoring:**
  Options are scored to estimate their attractiveness based on annualized return, adjusted for assignment risk. The score formula is:

   `score = (1 - |Δ|) × (250 / (DTE + 5)) × (bid price / strike price)`

  Where:

  * $\Delta$ = option delta (a rough proxy for the probability of assignment)
  * DTE = days to expiration
  * The factor 250 approximates the number of trading days in a year
  * Adding 5 days to DTE smooths the score for near-term options

* **Option Selection:**
  From all scored options, the strategy picks the highest-scoring contract per underlying symbol to promote diversification. It filters out options scoring below `SCORE_MIN` and returns either the top N options or all qualifying options.

---

## Ideas for Customization

### Stock Picking

* Use technical indicators such as moving averages, RSI, or support/resistance levels to identify stocks likely to remain range-bound — ideal for selling options in the Wheel strategy.
* Incorporate fundamental filters like earnings growth, dividend history, or volatility to select stocks you’re comfortable holding long term.

### Scoring Function for Puts / Calls

* Modify the scoring formula to weight factors differently or separately for puts vs calls. For example, emphasize calls with strikes just below resistance levels or puts on stocks with strong support.
* Consider adding factors like implied volatility or premium decay to better capture option pricing nuances.

### Managing a Larger Portfolio

* Allocate larger trade sizes to higher-scoring options for more efficient capital use.
* Allow multiple wheels per stock to increase position flexibility.
* Set exposure limits per underlying or sector to manage risk.

### Stop Loss When Puts Get Assigned

* Implement logic to cut losses if a stock price falls sharply after assignment, protecting capital from downside.

### Rolling Short Puts as Expiration Nears

* Instead of letting puts expire or get assigned, roll them forward to the next expiration or down to lower strikes to capture additional premium and manage risk.
* (For more, see [this Learn article](https://alpaca.markets/learn/options-wheel-strategy).)

---

## Final Notes

This is a great starting point for automating your trading, but always double-check your live trades — no system is completely hands-off.

Happy wheeling! 🚀
