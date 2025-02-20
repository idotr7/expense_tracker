from models import (Users, 
                    UserCreate, 
                    UserPublic, 
                    UserUpdate, 
                    Expense, 
                    ExpenseCreate, 
                    ExpensePublic, 
                    ExpenseUpdate, 
                    access_token, 
                    TimeFilter,
                    UsersPublicWithExpense,
                    ExpensePublicWithUsers)
from db import create_db_and_tables, get_session
from auth import verify, hash_password, create_access_token, get_current_user

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get('/')
def sanity():
    return "Health check"

@app.post('/login', response_model=access_token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # Use OAuth2 form instead of UserLogin
    session: Session = Depends(get_session)
):
    # 1. Validate credentials
    user = session.exec(select(Users).where(Users.email == form_data.username)).first()
    if not user or not verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data = {'user_id': user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post('/users/', response_model = UserPublic)
def create_user(*, session: Session = Depends(get_session), user: UserCreate):
    hashed_password = hash_password(user.password)
    extra_data = {"hashed_password": hashed_password}
    db_user = Users.model_validate(user, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get('/users/', response_model= list[UserPublic])
def read_users(*, session: Session = Depends(get_session)):
    users = session.exec(select(Users)).all()
    return users
        
@app.get('/users/{user_id}', response_model=UsersPublicWithExpense)
def read_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(Users,user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch('/users/{user_id}', response_model=UserPublic)
def update_user(*, session: Session = Depends(get_session), user_id:int, user: UserUpdate):
    db_user = session.get(Users,user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = hash_password(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
        
@app.post('/expenses/', response_model = ExpensePublic, status_code = 201)
def create_expense(*, 
                   session: Session = Depends(get_session), 
                   current_user: Users = Depends(get_current_user), 
                   expense: ExpenseCreate
                   ):
    db_expense = Expense.model_validate(expense, update= {"user_id":current_user.id})
    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense
        
@app.get('/expenses/{expense_id}', response_model=ExpensePublicWithUsers)
def read_expense_id(*, 
                    session: Session = Depends(get_session),
                    current_user: Users = Depends(get_current_user), 
                    expense_id: int):
    print(f"Fetching expense {expense_id} for user {current_user.id}")  # Debug log
    
    # First verify the expense exists at all
    expense = session.get(Expense, expense_id)
    if not expense:
        print(f"No expense found with ID {expense_id}")  # Debug log
        raise HTTPException(status_code=404, detail="Expense not found")
        
    # Then check if it belongs to the current user
    if expense.user_id != current_user.id:
        print(f"Expense {expense_id} belongs to user {expense.user_id}, not {current_user.id}")  # Debug log
        raise HTTPException(status_code=404, detail="Expense not found")
        
    return expense

@app.get('/expenses/', response_model=list[ExpensePublic])
def read_expense(*, 
                session: Session = Depends(get_session),
                current_user: Users = Depends(get_current_user), 
                time_filter: TimeFilter = Query(default=TimeFilter.ALL),
                custom:Optional[int] = Query(default=None,ge=1)):
    query = select(Expense).where(Expense.user_id == current_user.id)

    now = datetime.now()
    if time_filter == TimeFilter.PAST_WEEK:
        query = query.where(Expense.date >= now - timedelta(days=7))
    elif time_filter == TimeFilter.PAST_MONTH:
        query = query.where(Expense.date >= now - timedelta(days=30))
    elif time_filter == TimeFilter.LAST_3_MONTHS:
        query = query.where(Expense.date >= now - timedelta(days=90))
    elif time_filter == TimeFilter.CUSTOM:
        if not custom:
           raise HTTPException(status_code=404, detail="custom_days parameter is required when using CUSTOM filter") 
        query = query.where(Expense.date >= now - timedelta(days=custom))
            
    expenses = session.exec(query).all()
    if not expenses:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expenses
    
@app.patch('/expenses/{expense_id}', response_model=ExpensePublic)
def update_expense(*, 
                   session: Session = Depends(get_session),
                   current_user: Users = Depends(get_current_user), 
                   expense_id:int, 
                   expense: ExpenseUpdate):
    db_expense = session.exec(select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id)).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense_data = expense.model_dump(exclude_unset=True)
    db_expense.sqlmodel_update(expense_data)
    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense

@app.delete('/expenses/{expense_id}')
def delete_expense(*, 
                   session: Session = Depends(get_session), 
                   current_user: Users = Depends(get_current_user), 
                   expense_id:int):
    expense = session.exec(select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id)).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    session.delete(expense)
    session.commit()
    return f"Expense ID {expense_id} Deleted"