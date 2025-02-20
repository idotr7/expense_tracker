from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class UserBase(SQLModel):
    name:str = Field(index=True)
    email:EmailStr = Field(unique=True)
    
class Users(UserBase, table=True):
    id:int | None = Field(default=None, primary_key=True)
    last_updated:datetime = Field(default= datetime.now(),index=True) 
    hashed_password:str = Field()
    expenses: list["Expense"] = Relationship(back_populates="user")
    
class UserCreate(UserBase):
    password:str
    
class UserPublic(UserBase):
    id:int
    last_updated:datetime
    
class UserUpdate(SQLModel):
    name:str| None = None
    email:EmailStr | None = None
    password:str| None = None
    last_updated:datetime = Field(default= datetime.now()) 

class UserLogin(BaseModel):     
  email: EmailStr     
  password: str

class Category(str, Enum):
    GROCERIES = "Groceries"
    LEISURE = "Leisure"
    ELECTRONICS = "Electronics"
    UTILITIES = "Utilities"
    CLOTHING = "Clothing"
    HEALTH = "Health"
    OTHERS = "Others"

class ExpenseBase(SQLModel):
    amount: float  
    description: str
    category: Category
    user_id: int | None = Field(default=None, foreign_key="users.id")


class Expense(ExpenseBase, table = True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now)
    user: Users | None = Relationship(back_populates="expenses")
    
    
class ExpenseCreate(ExpenseBase):
    pass

class ExpensePublic(ExpenseBase):
    id: int
    date: datetime
    
class ExpenseUpdate(SQLModel):
    amount: float | None = None
    description: str| None = None
    category: Category | None = None

class TimeFilter(str, Enum):
    ALL = "all"
    PAST_WEEK = "past_week"
    PAST_MONTH = "past_month"
    LAST_3_MONTHS = "last_3_months"
    CUSTOM = "custom"
    
class UsersPublicWithExpense(UserPublic):
    expenses: list[ExpensePublic] | None = None    

class ExpensePublicWithUsers(ExpensePublic):
    user: UserPublic | None = None
    
class access_token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[str] = None
    
