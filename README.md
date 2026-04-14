## Group Members
Liam Proudford = 124774889
Evan Clinton = 124342216
Adam O Donnell = 124484992
Andrew Horgan = 124445536

A Flask web application that displays Star Wars characters from the SWAPI API, with a leaderboard backed by Supabase.
Features

Browse Star Wars characters
Leaderboard powered by Supabase
Health and status endpoints
Error handling with dedicated error page

## Tech Stack

Backend: Python, Flask
Database: Supabase (PostgreSQL via REST API)
External API: SWAPI
Config: python-dotenv

## Project Structure
AAEL/
├── app.py
├── .env.example
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── characters.html
    ├── leaderboard.html
    ├── compare.html
    ├── compare_results.html
    ├── compare_stats.html
    └── error.html

## Setup
1. Clone the repository
 https://github.com/liamproudford/AAEL.git


Install dependencies: pip install -r requirements.txt


## Run the app
App runs at http://127.0.0.1:5000
Live Link at https://aael.onrender.com/
Routes
/ = Home page
/characters = Browse Star Wars characters
/leaderboard = Top 10 leaderboard scores
/test-db = Test Supabase connection
/health = Health check
/status = Status of DB and SWAPI 

## Environment Variables
SUPABASE_URL = https://rblqmvwfcafamcikfxsr.supabase.co
URLSUPABASE_KEY = sb_publishable_I9J0cAhnhA_82BMp_BHbYw_MaBeReVF