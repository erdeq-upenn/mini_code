"""Black-Scholes pricing and Greeks. All functions are stateless."""

from __future__ import annotations

import math

from scipy.stats import norm


def _d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
    return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))


def _d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
    return _d1(S, K, T, r, sigma) - sigma * math.sqrt(T)


def price(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Theoretical Black-Scholes option price."""
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    disc = math.exp(-r * T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * disc * norm.cdf(d2)
    else:
        return K * disc * norm.cdf(-d2) - S * norm.cdf(-d1)


def delta(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Rate of change of option price with respect to spot (dV/dS)."""
    d1 = _d1(S, K, T, r, sigma)
    if option_type == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1.0


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Rate of change of delta with respect to spot (d²V/dS²). Same for call/put."""
    d1 = _d1(S, K, T, r, sigma)
    return norm.pdf(d1) / (S * sigma * math.sqrt(T))


def theta(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Time decay per calendar day (dV/dt / 365)."""
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    disc = math.exp(-r * T)
    term1 = -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
    if option_type == "call":
        annualised = term1 - r * K * disc * norm.cdf(d2)
    else:
        annualised = term1 + r * K * disc * norm.cdf(-d2)
    return annualised / 365.0


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Sensitivity to 1 percentage point change in vol (dV/dσ / 100). Same for call/put."""
    d1 = _d1(S, K, T, r, sigma)
    return S * norm.pdf(d1) * math.sqrt(T) / 100.0


def rho(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Sensitivity to 1 percentage point change in risk-free rate (dV/dr / 100)."""
    d2 = _d2(S, K, T, r, sigma)
    disc = math.exp(-r * T)
    if option_type == "call":
        return K * T * disc * norm.cdf(d2) / 100.0
    else:
        return -K * T * disc * norm.cdf(-d2) / 100.0


def all_greeks(
    S: float, K: float, T: float, r: float, sigma: float, option_type: str
) -> dict[str, float]:
    """Return all Greeks in a single dict."""
    return {
        "delta": delta(S, K, T, r, sigma, option_type),
        "gamma": gamma(S, K, T, r, sigma),
        "theta": theta(S, K, T, r, sigma, option_type),
        "vega": vega(S, K, T, r, sigma),
        "rho": rho(S, K, T, r, sigma, option_type),
    }
