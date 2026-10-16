"""Data model of telos.

Layer A: what is written on the document (output of the extraction / LLM).
Layer B: what customs clearance needs (output of the rule engine).
"""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


# ---------- Layer A: what is written on the document ----------

class Variant(BaseModel):
    """A sub-position of an invoice item, e.g. 'strawberry'."""
    description: str
    quantity: int = Field(ge=0)
    value: Decimal = Field(ge=0)


class InvoiceItem(BaseModel):
    """One item line on the invoice."""
    article_number: str | None = None
    trade_unit_gtin: str | None = None
    description: str
    cartons: int = Field(ge=0)
    variants: list[Variant] = []

    @model_validator(mode="after")
    def require_article_number_or_gtin(self):
        if not self.article_number and not self.trade_unit_gtin:
            raise ValueError("article_number or trade_unit_gtin is required")
        return self


class Invoice(BaseModel):
    """Header and item data extracted from an invoice."""
    invoice_number: str
    invoice_date: date
    currency: str = "EUR"
    goods_value_total: Decimal = Field(ge=0)
    net_mass_total: Decimal = Field(ge=0)
    gross_mass_total: Decimal = Field(ge=0)
    items: list[InvoiceItem]


# ---------- Layer B: what customs clearance needs ----------

class CustomsPosition(BaseModel):
    """A finished position for the customs declaration."""
    article_number: str
    tariff_number: str
    cartons: int
    net_mass: Decimal
    gross_mass: Decimal
    value: Decimal
