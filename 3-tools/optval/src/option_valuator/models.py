from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, model_validator


class OptionInput(BaseModel):
    ticker: str
    spot: float
    strike: float
    quote_date: date
    expiry_date: date
    option_type: Literal["call", "put"]
    option_price: float
    risk_free_rate: float = 0.05

    @model_validator(mode="after")
    def expiry_after_quote(self) -> OptionInput:
        if self.expiry_date <= self.quote_date:
            raise ValueError("expiry_date must be strictly after quote_date")
        if self.spot <= 0:
            raise ValueError("spot must be positive")
        if self.strike <= 0:
            raise ValueError("strike must be positive")
        if self.option_price < 0:
            raise ValueError("option_price must be non-negative")
        return self

    @property
    def time_to_expiry(self) -> float:
        """Years to expiry using actual/365.25 convention."""
        return (self.expiry_date - self.quote_date).days / 365.25


class ValuationResult(BaseModel):
    # --- inputs ---
    ticker: str
    quote_date: date
    expiry_date: date
    option_type: Literal["call", "put"]
    spot: float
    strike: float
    risk_free_rate: float
    option_price: float
    time_to_expiry: float
    # --- outputs ---
    implied_vol: float
    theoretical_price: float
    delta: float
    gamma: float
    theta: float   # per calendar day
    vega: float    # per 1 percentage point of vol
    rho: float     # per 1 percentage point of rate
    # --- seller return ---
    seller_collateral: float   # spot (call) or strike (put)
    seller_simple_return: float     # premium / collateral
    seller_annualized_return: float  # simple_return * 365 / days_to_expiry
    created_at: str
