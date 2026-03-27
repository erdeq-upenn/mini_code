"""Implied volatility solver using Brent's bracketing method."""

from __future__ import annotations

import math

from scipy.optimize import brentq

from . import pricing


def implied_vol(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str,
    tol: float = 1e-8,
    max_iter: int = 500,
) -> float:
    """
    Solve for implied volatility given a market option price.

    Returns IV as a decimal (e.g. 0.20 means 20% vol).

    Raises ValueError if the market price is outside no-arbitrage bounds.
    """
    disc = math.exp(-r * T)

    if option_type == "call":
        lower_bound = max(S - K * disc, 0.0)
        upper_bound = S
    else:
        lower_bound = max(K * disc - S, 0.0)
        upper_bound = K * disc

    if market_price < lower_bound - 1e-6:
        raise ValueError(
            f"Market price {market_price:.4f} is below the no-arbitrage lower bound "
            f"{lower_bound:.4f} for a {option_type}."
        )
    if market_price > upper_bound + 1e-6:
        raise ValueError(
            f"Market price {market_price:.4f} exceeds the no-arbitrage upper bound "
            f"{upper_bound:.4f} for a {option_type}."
        )

    def objective(sigma: float) -> float:
        return pricing.price(S, K, T, r, sigma, option_type) - market_price

    try:
        iv = brentq(objective, 1e-6, 10.0, xtol=tol, maxiter=max_iter)
    except ValueError as exc:
        raise ValueError(
            f"Could not solve for implied volatility. "
            f"Check inputs (spot={S}, strike={K}, T={T:.4f}, r={r}, "
            f"price={market_price}, type={option_type}). Detail: {exc}"
        ) from exc

    return iv
