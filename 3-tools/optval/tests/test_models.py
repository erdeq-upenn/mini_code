"""Tests for pricing, IV solver, and models."""

from __future__ import annotations

import math
from datetime import date

import pytest

from option_valuator.models import OptionInput
from option_valuator import pricing
from option_valuator.iv import implied_vol


# ---------------------------------------------------------------------------
# Black-Scholes price sanity checks
# ---------------------------------------------------------------------------

def test_call_price_atm():
    """ATM call should be positive and less than spot."""
    p = pricing.price(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type="call")
    assert 0 < p < 100


def test_put_price_atm():
    p = pricing.price(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type="put")
    assert 0 < p < 100


def test_put_call_parity():
    """C - P = S - K*e^(-rT)."""
    S, K, T, r, sigma = 100.0, 105.0, 0.5, 0.04, 0.25
    c = pricing.price(S, K, T, r, sigma, "call")
    p = pricing.price(S, K, T, r, sigma, "put")
    parity = S - K * math.exp(-r * T)
    assert abs((c - p) - parity) < 1e-8


def test_deep_itm_call_approaches_forward():
    """Deep ITM call ~ S - K*e^(-rT)."""
    S, K, T, r, sigma = 200.0, 100.0, 1.0, 0.05, 0.2
    c = pricing.price(S, K, T, r, sigma, "call")
    fwd = S - K * math.exp(-r * T)
    assert abs(c - fwd) < 0.5


# ---------------------------------------------------------------------------
# Greeks
# ---------------------------------------------------------------------------

def test_call_delta_between_0_and_1():
    d = pricing.delta(100, 100, 1.0, 0.05, 0.2, "call")
    assert 0 < d < 1


def test_put_delta_between_minus1_and_0():
    d = pricing.delta(100, 100, 1.0, 0.05, 0.2, "put")
    assert -1 < d < 0


def test_gamma_positive():
    g = pricing.gamma(100, 100, 1.0, 0.05, 0.2)
    assert g > 0


def test_call_theta_negative():
    """Call theta is negative — time decay."""
    th = pricing.theta(100, 100, 1.0, 0.05, 0.2, "call")
    assert th < 0


def test_vega_positive():
    v = pricing.vega(100, 100, 1.0, 0.05, 0.2)
    assert v > 0


def test_call_rho_positive():
    rh = pricing.rho(100, 100, 1.0, 0.05, 0.2, "call")
    assert rh > 0


def test_put_rho_negative():
    rh = pricing.rho(100, 100, 1.0, 0.05, 0.2, "put")
    assert rh < 0


# ---------------------------------------------------------------------------
# Implied volatility round-trip
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sigma", [0.1, 0.2, 0.35, 0.6])
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_iv_roundtrip(sigma, option_type):
    """Solving IV from a theoretical price should recover the input sigma."""
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    mkt_price = pricing.price(S, K, T, r, sigma, option_type)
    solved = implied_vol(mkt_price, S, K, T, r, option_type)
    assert abs(solved - sigma) < 1e-5


def test_iv_raises_on_arbitrage_price():
    with pytest.raises(ValueError, match="no-arbitrage"):
        implied_vol(market_price=200.0, S=100.0, K=100.0, T=1.0, r=0.05, option_type="call")


# ---------------------------------------------------------------------------
# OptionInput model
# ---------------------------------------------------------------------------

def test_option_input_expiry_before_quote_raises():
    with pytest.raises(Exception):
        OptionInput(
            ticker="AAPL",
            spot=100, strike=100,
            quote_date=date(2026, 6, 1),
            expiry_date=date(2026, 5, 1),
            option_type="call",
            option_price=5.0,
        )


def test_option_input_time_to_expiry():
    inp = OptionInput(
        ticker="AAPL",
        spot=100, strike=100,
        quote_date=date(2026, 1, 1),
        expiry_date=date(2027, 1, 1),
        option_type="call",
        option_price=5.0,
    )
    assert abs(inp.time_to_expiry - 1.0) < 0.01


def test_option_input_ticker_uppercased_via_cli():
    """Ticker is stored as-is in the model; CLI uppercases before passing in."""
    inp = OptionInput(
        ticker="aapl",
        spot=100, strike=100,
        quote_date=date(2026, 1, 1),
        expiry_date=date(2027, 1, 1),
        option_type="call",
        option_price=5.0,
    )
    assert inp.ticker == "aapl"  # model doesn't enforce case; CLI does
