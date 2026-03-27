"""CLI entry point — `optval price` and `optval history`."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from pydantic import ValidationError
from rich.console import Console

from . import pricing, iv as iv_module
from .db import DEFAULT_DB_PATH, fetch_history, insert_valuation
from .formatters import print_history, print_valuation
from .models import OptionInput, ValuationResult

app = typer.Typer(
    name="optval",
    help="Black-Scholes option pricer with all Greeks and implied volatility.",
    add_completion=False,
)
err_console = Console(stderr=True)


@app.command()
def price(
    ticker: Annotated[str, typer.Option("--ticker", "-u", help="Underlying ticker symbol (e.g. AAPL)")],
    spot: Annotated[float, typer.Option("--spot", "-s", help="Current spot / underlying price")],
    strike: Annotated[float, typer.Option("--strike", "-k", help="Option strike price")],
    expiry: Annotated[str, typer.Option("--expiry", "-e", help="Expiry date  YYYY-MM-DD")],
    option_type: Annotated[str, typer.Option("--type", "-t", help="'call' or 'put'")],
    option_price: Annotated[float, typer.Option("--price", "-p", help="Market option price (used to solve IV)")],
    quote_date: Annotated[Optional[str], typer.Option("--quote-date", "-q", help="Quote date YYYY-MM-DD (default: today)")] = None,
    risk_free_rate: Annotated[float, typer.Option("--rate", "-r", help="Annual risk-free rate as decimal (default 0.05)")] = 0.05,
    no_save: Annotated[bool, typer.Option("--no-save", help="Skip saving result to database")] = False,
    db: Annotated[Optional[Path], typer.Option("--db", help="SQLite database path")] = None,
) -> None:
    """Price an option, solve for implied volatility, and display all Greeks."""
    db_path = db or DEFAULT_DB_PATH
    qdate = date.fromisoformat(quote_date) if quote_date else date.today()

    try:
        inp = OptionInput(
            ticker=ticker.upper(),
            spot=spot,
            strike=strike,
            quote_date=qdate,
            expiry_date=date.fromisoformat(expiry),
            option_type=option_type.lower(),
            option_price=option_price,
            risk_free_rate=risk_free_rate,
        )
    except (ValidationError, ValueError) as exc:
        err_console.print(f"[red]Input error:[/red] {exc}")
        raise typer.Exit(1)

    T = inp.time_to_expiry
    S, K, r = inp.spot, inp.strike, inp.risk_free_rate

    try:
        iv = iv_module.implied_vol(inp.option_price, S, K, T, r, inp.option_type)
    except ValueError as exc:
        err_console.print(f"[red]IV solver error:[/red] {exc}")
        raise typer.Exit(1)

    theo = pricing.price(S, K, T, r, iv, inp.option_type)
    greeks = pricing.all_greeks(S, K, T, r, iv, inp.option_type)

    days = (inp.expiry_date - inp.quote_date).days
    collateral = S if inp.option_type == "call" else K
    simple_ret = inp.option_price / collateral
    annualized_ret = simple_ret * (365 / days)

    result = ValuationResult(
        ticker=inp.ticker,
        quote_date=inp.quote_date,
        expiry_date=inp.expiry_date,
        option_type=inp.option_type,
        spot=S,
        strike=K,
        risk_free_rate=r,
        option_price=inp.option_price,
        time_to_expiry=T,
        implied_vol=iv,
        theoretical_price=theo,
        seller_collateral=collateral,
        seller_simple_return=simple_ret,
        seller_annualized_return=annualized_ret,
        created_at=datetime.now().isoformat(timespec="seconds"),
        **greeks,
    )

    print_valuation(result)

    if not no_save:
        row_id = insert_valuation(result, db_path)
        err_console.print(f"[dim]Saved to database (id={row_id}, path={db_path})[/dim]")


@app.command()
def history(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Number of recent records to show")] = 20,
    db: Annotated[Optional[Path], typer.Option("--db", help="SQLite database path")] = None,
) -> None:
    """Show recent valuations from the database."""
    db_path = db or DEFAULT_DB_PATH
    rows = fetch_history(limit=limit, db_path=db_path)
    print_history(rows)


if __name__ == "__main__":
    app()
