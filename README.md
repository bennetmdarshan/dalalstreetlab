# Dalal Street Lab

A Wall Street-inspired investing studio for BSE educational paper trading. Dark green terminal navigation, an animated ticker, warm editorial typography, responsive charts and a fully browser-local ledger. There is no brokerage connection and no real money.

## Start here

1. Extract the ZIP.
2. Open a terminal inside `dalal-street-lab`.
3. Run `python -m http.server 8000` (Windows) or `python3 -m http.server 8000` (macOS/Linux).
4. Open **http://localhost:8000**.

Opening `index.html` by double-click is not supported: browsers restrict module imports and JSON fetching from file URLs. Python is needed only to serve files locally or fetch data; the deployed app needs no Python server or build system.

## Host on GitHub Pages

The repository root should contain `index.html`, `app.js`, `engine.js`, `style.css`, `data.json` and `favicon.svg`. Do not upload the ZIP itself or place these files under an extra nested folder.

**Simple browser upload:** create a GitHub repository, upload the extracted contents, then open **Settings → Pages → Build and deployment → Deploy from a branch → main → / (root) → Save**. GitHub will display your site URL after deployment, typically `https://YOUR-USERNAME.github.io/YOUR-REPO/`. This buildless app uses relative paths and works at that URL.

**With the included workflow:** upload `.github/workflows/pages.yml`, choose **GitHub Actions** as the Pages source, and run **Publish practice floor**. The workflow runs calculation tests and publishes only the public static files. There is no API key and no frontend package installation.

GitHub's official setup guide: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site

## What you can do

- Buy and sell whole shares with virtual money; review a quote before confirming.
- Start with three independent ₹1,00,000 portfolios; create up to 20, rename them, and compare returns over a common date window.
- Set one optional automatic rule per portfolio: buy-and-hold, SMA trend, or RSI mean reversion. Choose a stock and a 5–100% entry size. Rules run only when you advance replay sessions, not while the page is closed.
- Inspect daily OHLC candles, volume, 20/50-session simple averages, Wilder RSI (14), MACD (12/26/9), and prior 20-session range breakouts.
- Explore complementary exposure using different sectors and 60-session daily-return correlations.
- Run all three strategy backtests on the same stock, dates and initial capital. Compare net equity, return, drawdown and fill count.
- Record a thesis for each manual trade and review the journal.
- Complete six short investing lessons with knowledge checks.
- Export and restore a complete experiment, including its dataset. State stays in this browser; there is no account or server sync.

Portfolio strategy names are labels until an automatic rule is explicitly enabled. Automatic exits sell the entire selected position, including manually purchased shares in that stock. The rule does not rebalance other holdings.

## Important: included data versus actual BSE data

**The shipped `data.json` is a deterministic, synthetic fixture.** The companies and BSE identifiers are real; prices, volumes and sessions are fictitious. Weekends are omitted, but exchange holidays are not modelled. The app displays “ILLUSTRATIVE DATA” prominently, and synthetic results are never presented as actual historical performance.

**This release does not provide live BSE prices.** SEBI's 8 May 2026 circular prescribes a 30-day lag for educational market data, applicable from 1 July 2026. This project's educational replay therefore enforces a minimum 30-day age; the fetch script uses a conservative 31-day cutoff. Indicator conditions explain historical observations rather than recommend actual purchases or sales.

Official circular: https://www.sebi.gov.in/sebi_data/attachdocs/may-2026/1778242522289.pdf

Free/open-source software is not the same as freely redistributable exchange data. The included personal-use integration uses **yfinance**, an open-source client for Yahoo Finance's unofficial endpoints. No API key is needed, but access, symbol coverage and rate limits can change. yfinance's documentation states that downloaded data is subject to Yahoo's terms and intended for personal use. It is not an official BSE feed.

Source and terms: https://github.com/ranaroussi/yfinance

## Get actual BSE historical prices for your browser

Recommended personal-use route, from your local project folder:

```sh
python -m pip install -r requirements.txt
python scripts/fetch_bse.py --output bse-history.json
```

Use `python3` if that is your system's Python command. The script checks BSE exchange metadata, INR currency, valid OHLCV and aligned dates, fetching twelve BSE stocks. It will fail rather than substitute NSE data or invent missing prices. Existing output is preserved if the fetch fails. The Python dependency is version-bounded but not locked; provider changes can still require updates.

Then open **Data & settings → Import data file**, choose `bse-history.json`, export the current experiment if desired, and start the new replay. Actual history is stored locally in your browser; it is not automatically published with the website. Importing different prices resets portfolios because mixing price histories would invalidate the ledger.

Optional GitHub route: run **Fetch personal BSE history** from Actions in a **private repository**, download the `bse-history-personal-use` artifact, unzip it, and import the JSON into the app. The workflow does not commit data or deploy it. Avoid running it in a public repository without appropriate data rights: artifacts can be accessible to others. The workflow is manual, not a scheduled service.

The repository's public site can keep shipping the synthetic fixture while your browser imports actual historical data. `bse-history.json` is excluded from Git by default.

### Other authorized API providers

You can enter a CORS-enabled HTTPS dataset endpoint in **Data & settings**, or import its JSON. The app validates the response before offering to start a new experiment. An endpoint failure leaves the existing experiment intact.

The endpoint must return this schema:

```json
{
  "version": 1,
  "id": "unique-content-version-id",
  "mode": "historical",
  "source": "Provider and provenance",
  "priceBasis": "Describe adjustments and currency",
  "stocks": [
    {
      "symbol": "RELIANCE.BO",
      "name": "Reliance Industries",
      "sector": "Energy",
      "code": "500325",
      "bars": [
        {"date": "2025-01-02", "o": 1200, "h": 1210, "l": 1190, "c": 1205, "v": 1000000}
      ]
    }
  ]
}
```

The example is structural, not an actual quote. Valid datasets need 2–100 distinct `.BO` stocks, 100–5000 daily bars per stock, exactly aligned ascending session dates, finite valid OHLCV, and no dates in the preceding 30 days. Dataset IDs must change whenever the data changes. App download/import size limit is 8 MB. Do not embed API secrets in public JavaScript; use an authorized server-side adapter for providers that need a secret. Generic endpoints must document price adjustments honestly; the built-in fetch script supplies adjusted prices.

## Execution & performance model

- **Manual fills:** the visible replay close, adjusted for 0.05% adverse slippage, plus a fee of 0.10% of gross value on each side. Fill prices, fees, cash and cost basis are rounded to ₹0.01. This is a model, not BSE tick-size emulation.
- **Automatic and backtest fills:** a signal from a completed session is executed at the following session's open. Costs match manual fills. No future prices are used to generate signals.
- **Position accounting:** cash + marked holdings = equity. Weighted-average entry cost includes fees; realized P&L deducts allocated cost basis and exit fees. No shorting, leverage, fractional shares or external cash flows.
- **Auto sizing:** new entries use the configured fraction of prior-close equity, capped by cash. One selected-stock position at a time, no pyramiding. Buy-and-hold enters once; disabling it does not liquidate a position.
- **Backtest comparison:** ₹1,00,000 each, 50-session shared warm-up, common evaluation dates. The baseline places its first order after warm-up and fills next session. Returns include costs; open positions are marked rather than forcibly liquidated. Final pending signals do not get a fabricated fill.
- **Adjusted prices:** yfinance uses `auto_adjust=True` for splits and distributions. Holdings represent educational adjusted-price units. Dividends are not separately credited and historical raw share quantities are not reconstructed.
- **Excluded:** broker order books, spread modelling beyond fixed slippage, liquidity constraints, bid/ask ticks, intraday stops, live orders, taxes, settlement, fundamental-data screening and index benchmark data.
- **Risk:** historical correlation can change, breakout rules can fail, and backtests can overfit. A maximum-return result is not automatically the best strategy.

## Verification

```sh
npm test
python -m unittest discover -s tests -p 'test_*.py'
```

No JavaScript dependency installation is needed for `npm test`.

This release passed 13 calculation/ledger tests and 3 Python data-normalization tests. They check order accounting, invalid orders, price/return indicators, drawdown, next-open execution, invariance to unseen future prices, dataset constraints, corruption rejection, automatic sizing and ledger restoration.

A separate simulated-DOM smoke check passed startup, stock search, order review, buy/sell fills, oversell protection, replay stepping, portfolio creation, automatic rules, strategy results, lessons, name escaping and restart with saved-state reconciliation. Native browser visual QA was unavailable in the build environment; desktop/mobile layouts still need a real-browser review after hosting.

**External data verification limit:** direct Yahoo access returned a rate-limit response during development, and a third-party free endpoint did not provide usable BSE data. The live network path was therefore not successfully verified end-to-end. The project ships visibly synthetic practice data and a validated fetch pipeline, not a claim of a working live exchange connection. Try the personal data workflow from your own network; failures are explicit and never silently become fabricated historical prices.

## Files

- `index.html`, `style.css`: responsive trading-floor interface.
- `app.js`: interaction, portfolio persistence, lessons, data loading and charts.
- `engine.js`: pure indicators, trade accounting, backtesting and validators.
- `data.json`: clearly labelled synthetic practice fixture.
- `scripts/fetch_bse.py`: personal-use BSE historical-data fetch.
- `scripts/make_demo.py`: reproducible fixture generator.
- `tests/`: calculation, accounting and normalization tests.
- `.github/workflows/`: static Pages publishing and manual personal-data fetch.

App source code is MIT licensed. This does not change any market-data provider's terms. Google Fonts are an optional online visual enhancement; system fonts are supplied as fallbacks. No analytics or brokerage SDKs are included.
