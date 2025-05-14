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

2. **Install the required packages:**

   ```bash
   pip install -e .
   ```

3. **Set up your API credentials:**

   Create a file named `credentials.py` inside the `config/` folder with the following content:

   ```python
   ALPACA_API_KEY = 'YOUR_PUBLIC_KEY'
   ALPACA_SECRET_KEY = 'YOUR_PRIVATE_KEY'
   IS_PAPER = True  # Set to False if using a live account
   ```

4. **Choose your symbols:**

   The strategy trades only the symbols listed in `config/symbol_list.txt`. Edit this file to include the tickers you want to run the Wheel strategy on — one symbol per line. Choose stocks you'd be comfortable holding long-term.

5. **Configure trading parameters:**

   Adjust values in `config/params.py` to customize things like buying power limits, options characteristics (greeks / expiry), and scoring thresholds. Each parameter is documented in the file.

### 6. **Run the strategy:**

```bash
run-strategy
```

By default, the script assumes your portfolio is empty or fully managed by this strategy.

If you want to **liquidate all existing positions before running**, you can use the `--fresh-start` flag:

```bash
run-strategy --fresh-start
```

⚠️ **Warning:** This will immediately close **all open positions** in the account. Use this only on the **first run**.


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

## Ideas for Customization

### Stock Picking

* Use resistance levels, moving averages, RSI, etc. to identify stocks that are likely to stay range bound (ideal for the Wheel).
* Filter stocks based on earnings growth, dividend history, volatility, or whatever you like to find companies that you would be comfortable holding long term. 

### Scoring Function for Puts / Calls

* Tweak the way options are ranked.
* You might want separate logic for puts vs calls (different things matter, for example you might want to weight calls more heavily that are just below resistance levels).

### Managing a Larger Portfolio

* Weight bigger trades toward higher-scoring opportunities.
* Allow multiple wheels on the same stock.
* Set limits to avoid overexposure.

### Stop Loss When Puts Get Assigned

* Add logic to cut losses if a stock tanks after you're assigned.

### Rolling Short Puts as Expiration Nears

* Instead of letting puts expire or get assigned immediately, you could roll them to the next expiration to collect more premium.
* (See [this Learn article](https://alpaca.markets/learn/options-wheel-strategy) about rolling options for more.)

---

## Final Notes

This is a great starting point for automating your trading, but always double-check your live trades. No system is 100% hands-off yet.

Happy wheeling! 🚀
