"""Rich terminal output formatters."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .models import ValuationResult

console = Console()


def print_valuation(result: ValuationResult) -> None:
    # --- inputs panel ---
    inp = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    inp.add_column("Field", style="bold cyan")
    inp.add_column("Value", style="white")
    inp.add_row("Ticker", result.ticker)
    inp.add_row("Option Type", result.option_type.upper())
    inp.add_row("Quote Date", str(result.quote_date))
    inp.add_row("Expiry Date", str(result.expiry_date))
    inp.add_row("Time to Expiry", f"{result.time_to_expiry:.4f} yrs")
    inp.add_row("Spot Price", f"{result.spot:.4f}")
    inp.add_row("Strike Price", f"{result.strike:.4f}")
    inp.add_row("Market Price", f"{result.option_price:.4f}")
    inp.add_row("Risk-Free Rate", f"{result.risk_free_rate * 100:.2f}%")
    console.print(Panel(inp, title="[bold]Inputs", border_style="blue"))

    # --- pricing panel ---
    pri = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    pri.add_column("Field", style="bold green")
    pri.add_column("Value", style="white")
    pri.add_row("Implied Volatility", f"{result.implied_vol * 100:.4f}%")
    pri.add_row("Theoretical Price", f"{result.theoretical_price:.4f}")
    console.print(Panel(pri, title="[bold]Pricing", border_style="green"))

    # --- greeks panel ---
    grk = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    grk.add_column("Greek", style="bold yellow")
    grk.add_column("Value", style="white")
    grk.add_column("Interpretation", style="dim")
    grk.add_row("Delta", f"{result.delta:+.4f}", "price change per $1 move in spot")
    grk.add_row("Gamma", f"{result.gamma:+.6f}", "delta change per $1 move in spot")
    grk.add_row("Theta", f"{result.theta:+.4f}", "price change per calendar day")
    grk.add_row("Vega",  f"{result.vega:+.4f}",  "price change per 1% move in vol")
    grk.add_row("Rho",   f"{result.rho:+.4f}",   "price change per 1% move in rate")
    console.print(Panel(grk, title="[bold]Greeks", border_style="yellow"))

    # --- seller return panel ---
    collateral_label = "Spot (covered call)" if result.option_type == "call" else "Strike (cash-secured put)"
    sel = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    sel.add_column("Field", style="bold magenta")
    sel.add_column("Value", style="white")
    sel.add_row("Collateral Basis", f"{result.seller_collateral:.4f}  [{collateral_label}]")
    sel.add_row("Premium Collected", f"{result.option_price:.4f}")
    sel.add_row("Simple Return", f"{result.seller_simple_return * 100:.4f}%")
    sel.add_row("Annualized Return", f"{result.seller_annualized_return * 100:.4f}%")
    console.print(Panel(sel, title="[bold]Seller's Return", border_style="magenta"))


def print_history(rows: list[dict]) -> None:
    if not rows:
        console.print("[dim]No history found.[/dim]")
        return

    t = Table(
        "ID", "Ticker", "Date", "Type", "Spot", "Strike", "Expiry",
        "MktPx", "IV%", "ThPx", "Delta", "Gamma", "Theta", "Vega", "Rho",
        box=box.SIMPLE_HEAD,
        show_lines=False,
    )
    for r in rows:
        t.add_row(
            str(r["id"]),
            r["ticker"],
            r["quote_date"],
            r["option_type"].upper(),
            f"{r['spot']:.2f}",
            f"{r['strike']:.2f}",
            r["expiry_date"],
            f"{r['option_price']:.2f}",
            f"{r['implied_vol'] * 100:.2f}",
            f"{r['theoretical_price']:.2f}",
            f"{r['delta']:+.4f}",
            f"{r['gamma']:.6f}",
            f"{r['theta']:+.4f}",
            f"{r['vega']:+.4f}",
            f"{r['rho']:+.4f}",
        )
    console.print(t)
