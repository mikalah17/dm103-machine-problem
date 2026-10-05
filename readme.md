# Simple BPM System - Online Food Ordering

A Flask + MySQL app for taking food orders, tracking payment, and moving orders through preparation to completion.

## Requirements
- Python 3
- MySQL Server (running)
- MySQL Workbench (or any MySQL client)

## Setup
1. Install the packages:
```
   pip install -r requirements.txt
```
2. Open `schema.sql` in MySQL Workbench and run it once. This creates the `food_ordering_bpm` database and tables.
3. Set your MySQL login. Either edit `DB_CONFIG` at the top of `app.py`, or set environment variables (recommended, so you don't commit your password):

   Command Prompt:
```
   set DB_USER=root
   set DB_PASSWORD=your_mysql_password
```
   PowerShell:
```
   $env:DB_USER="root"
   $env:DB_PASSWORD="your_mysql_password"
```
4. Run the app:
```
   python app.py
```
5. Open http://127.0.0.1:5000

## Project structure
- `app.py` - routes and database logic
- `schema.sql` - database schema
- `templates/` - HTML pages
- `static/css/style.css` - styles