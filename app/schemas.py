from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List
from pydantic import BaseModel
from typing import Union
from pydantic import BaseModel, EmailStr



# ExpenseBase is the common structure for both create and read
class ExpenseBase(BaseModel): 
    category: str
    amount: float
    Note: Optional[str] = None

# ExpenseCreate is what the user sends when adding an expense
class ExpenseCreate(ExpenseBase):
    pass

# Expenseout is what your API returns (with id and timestamp)
class Expenseout(BaseModel):
    id : int
    Note: Optional[str] = None
    amount : float
    category : str
    timestamp : datetime

    class Config:
        from_attributes = True

class ExpenseSummary(BaseModel):
    total_amount: float
    expenses: List[Expenseout]
    message: Optional[str] = None

    class Config:
        from_attributes = True


# For POST request body
class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

# ---------------- category Schemas ----------------

class CategorySummary(BaseModel):
    category: str
    total_amount: float

class CategoryTotal(BaseModel):
    category: str
    total_amount: float

class CategorySummaryResponse(BaseModel):
    total_amount: float
    categories: List[CategoryTotal]

class ExpensesByCategoryRequest(BaseModel):
    category: str
    start_date: datetime
    end_date: datetime

class ExpensesByCategoryResponse(BaseModel):
    total_amount: float
    expenses: List[Expenseout]

# ---------------- Income Schemas ----------------
class IncomeBase(BaseModel):
    amount: float
    note: str | None = None

class IncomeCreate(IncomeBase):
    pass

class IncomeResponse(IncomeBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ---------------- Saving Schemas ----------------
class SavingBase(BaseModel):
    amount: float
    note: str | None = None

class SavingCreate(SavingBase):
    amount: float
    note: Optional[str] = None

class SavingResponse(SavingBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class Saving(SavingCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


# ---------------- summary Schemas ----------------


class MonthlySummary(BaseModel):
    month: str
    total_income: Union[float, str]
    total_expense: Union[float, str]
    total_saving: Union[float, str]
    balance: Union[float, str]


# ---------------- auth/user Schemas ----------------


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
   
