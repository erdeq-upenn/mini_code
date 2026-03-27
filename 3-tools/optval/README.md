# option-valuator

Black-Scholes option pricer with implied volatility solver, all Greeks, and a SQLite history log.

## Requirements

- [uv](https://docs.astral.sh/uv/) — handles Python version and dependencies

## Setup

```bash
git clone <repo>
cd option_valuator
uv sync
```

This creates a `.venv` and installs all dependencies. Python 3.12 is pinned automatically.

## Usage

### Price an option

```bash
uv run optval price \
  --ticker SPY \
  --spot 150 \
  --strike 155 \
  --expiry 2026-09-19 \
  --type call \
  --price 8.50
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--ticker` | `-u` | Underlying ticker symbol (e.g. `AAPL`) | required |
| `--spot` | `-s` | Current underlying price | required |
| `--strike` | `-k` | Strike price | required |
| `--expiry` | `-e` | Expiry date `YYYY-MM-DD` | required |
| `--type` | `-t` | `call` or `put` | required |
| `--price` | `-p` | Market option price (used to solve IV) | required |
| `--quote-date` | `-q` | Quote date `YYYY-MM-DD` | today |
| `--rate` | `-r` | Annual risk-free rate as decimal | `0.05` |
| `--no-save` | | Skip saving result to database | false |
| `--db` | | Custom SQLite database path | `data/option_valuator.db` |

**Output:** three panels — Inputs, Pricing (IV + theoretical price), Greeks.

### View history

```bash
uv run optval history
uv run optval history --limit 50
```

Shows recent valuations from the database in a table.

### Help

```bash
uv run optval --help
uv run optval price --help
uv run optval history --help
```

## Greeks reference

All Greeks follow Bloomberg conventions:

| Greek | Definition | Units |
|---|---|---|
| **Delta** | dV/dS | price change per $1 move in spot |
| **Gamma** | d²V/dS² | delta change per $1 move in spot |
| **Theta** | dV/dt | price change per **calendar day** |
| **Vega** | dV/dσ | price change per **1% move** in vol |
| **Rho** | dV/dr | price change per **1% move** in rate |

## Examples

```bash
# ATM call, SPY-like
uv run optval price -u SPY -s 550 -k 550 -e 2026-06-19 -t call -p 22.00 -r 0.045

# OTM put, with explicit quote date
uv run optval price -u SPY -s 550 -k 520 -e 2026-06-19 -t put -p 9.50 -q 2026-03-26

# Price without saving to DB
uv run optval price -u AAPL -s 100 -k 105 -e 2026-12-18 -t call -p 5.00 --no-save

# Use a custom DB file
uv run optval price -u TSLA -s 100 -k 100 -e 2026-09-18 -t put -p 4.00 --db ~/myoptions.db
uv run optval history --db ~/myoptions.db
```

## Run tests

```bash
uv run pytest
uv run pytest -v          # verbose
uv run pytest --cov       # with coverage
```

## Project structure

```
option_valuator/
├── pyproject.toml                  # dependencies and entry points
├── .python-version                 # Python 3.12 (managed by uv)
├── data/
│   └── option_valuator.db          # SQLite history (auto-created)
├── src/option_valuator/
│   ├── main.py                     # CLI (optval price / optval history)
│   ├── pricing.py                  # Black-Scholes price and Greeks
│   ├── iv.py                       # Implied volatility solver (Brent's method)
│   ├── models.py                   # Pydantic input/output models
│   ├── db.py                       # SQLite CRUD
│   └── formatters.py               # Rich terminal output
└── tests/
    └── test_models.py
```
