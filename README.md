# Expense Tracker API
https://roadmap.sh/projects/expense-tracker-api

A FastAPI-based expense tracking application that allows users to manage their expenses with authentication and filtering capabilities.

## Features

- User authentication with JWT tokens
- CRUD operations for expenses
- Expense categorization
- Time-based expense filtering
- PostgreSQL database integration

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- pip or uv package manager

## Installation

1. Clone the repository:
bash
git clone <repository-url>
cd expense-tracker-api

2. Install uv (if not already installed):
bash
pip install uv

3. Create and activate a virtual environment:
bash
uv venv
source .venv/bin/activate # On Unix/macOS
or
.venv\Scripts\activate # On Windows

4. Install dependencies using uv:
bash
uv sync


## Database Setup

1. Create a PostgreSQL database:
bash
createdb expense_tracker


2. Set up environment variables:
Create a `.env` file in the project root with the following content:
Database configuration
DB = ""
HOST = ""
USER = ""
PASSWORD = ""

SECRET_KEY = ""

## Running the Application

1. Start the FastAPI server:
bash
uvicorn app:app --reload (for development only)


The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /auth/register`: Register a new user
- `POST /auth/login`: Login and get access token

### Expenses
- `GET /expenses`: List all expenses
- `POST /expenses`: Create a new expense
- `GET /expenses/{expense_id}`: Get specific expense
- `PUT /expenses/{expense_id}`: Update an expense
- `DELETE /expenses/{expense_id}`: Delete an expense

## Filtering Expenses

You can filter expenses using query parameters:
- `category`: Filter by expense category
- `start_date`: Filter expenses after this date (YYYY-MM-DD)
- `end_date`: Filter expenses before this date (YYYY-MM-DD)

Example:GET /expenses?category=food&start_date=2024-01-01&end_date=2024-12-31
