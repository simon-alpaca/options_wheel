# Automated Wheel Strategy

Welcome to the Wheel Strategy automation project!
This script is designed to help you trade the classic "wheel" options strategy with as little manual work as possible.

---

## Strategy Logic

Here's the basic idea:

1. **Sell cash-secured puts** on stocks you wouldn't mind owning.
2. If you **get assigned**, buy the stock.
3. Then **sell covered calls** on the stock you own.
4. Keep collecting premiums until the stock gets called away.
5. Repeat the cycle!

This code helps pick the right puts and calls to sell, tracks your positions, and suggests next steps automatically.

---

## How to Run The Code

1. Install the required packages:

   ```bash
   pip install -e .
   ```

2. Make sure your broker API keys are set up correctly (you can use environment variables or a config file).

3. Then just run:

   ```bash
   run-strategy
   ```

The script will:

* Choose stocks to run the wheel on
* Score the best puts/calls to sell
* Track your open trades

---

## Automating the Wheel

### Setting Up a Cron Job

Want this to run automatically every day? Use a cron job!

1. Open your crontab:

   ```bash
   crontab -e
   ```

2. Add a line like this to run it on weekdays before market open:

   ```bash
   0 9 * * 1-5 /path/to/python /path/to/run_wheel.py >> /path/to/logfile.log 2>&1
   ```

If you need API keys or other environment variables, you might want to call a wrapper shell script that sets everything up before running Python.

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

## What You May Want to Customize / Improve

### Stock Picking

* Use resistance levels, moving averages, RSI, etc.
* Filter stocks based on earnings growth, dividend history, volatility, or whatever you like.

### Scoring Function for Puts / Calls

* Tweak the way options are ranked.
* You might want separate logic for puts vs calls (different things matter).

### Managing a Larger Portfolio

* Weight bigger trades toward higher-scoring opportunities.
* Allow multiple wheels on the same stock.
* Set limits to avoid overexposure.

### Stop Loss When Puts Get Assigned

* Add logic to cut losses if a stock tanks after you're assigned.

### Rolling Short Puts as Expiration Nears

* Instead of letting puts expire or get assigned immediately, you could roll them to the next expiration to collect more premium.
* (See [this Learn article](#) about rolling options for more.)

---

## Final Notes

This is a great starting point for automating your trading, but always double-check your live trades. No system is 100% hands-off yet.

Happy wheeling! 🚀
