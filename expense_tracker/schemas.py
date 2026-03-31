from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional

class ExpenseBase(BaseModel):
    description: str   = Field(..., min_length=1, max_length=255)
    amount:      float = Field(..., gt=0)
    date:        date

# Request
class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    description: Optional[str]  = Field(default=None, min_length=1, max_length=255)
    amount:      Optional[float] = Field(default=None, gt=0)
    date:        Optional[date]  = None

# Response
class ExpenseOut(ExpenseBase):
    id: int
    model_config = {"from_attributes": True}  # allows ORM → Pydantic conversion

# Report responses
class ShopSummary(BaseModel):
    shop:  str
    total: float

class PeriodTotal(BaseModel):
    period: str
    total:  float

class MonthTotal(BaseModel):
    month: int
    year:  int
    total: float

class YearTotal(BaseModel):
    year:  int
    total: float