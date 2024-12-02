from fastapi import FastAPI
from random import randint, uniform
import asyncio
import json
from pathlib import Path

app = FastAPI()

# Initialize data
teams = [
    {"id": 1, "name": "Commanders", "bias": 0.1},  # Biased to perform badly
    {"id": 2, "name": "Texans", "bias": 0.2},
    {"id": 3, "name": "Packers", "bias": 0.3},
    {"id": 4, "name": "Steelers", "bias": 0.4},
    {"id": 5, "name": "Vikings", "bias": 0.5},
    {"id": 6, "name": "Eagles", "bias": 0.6},
    {"id": 7, "name": "Bills", "bias": 0.7},
    {"id": 8, "name": "Chiefs", "bias": 0.8},
    {"id": 9, "name": "Lions", "bias": 0.9},
    {"id": 10, "name": "Ravens", "bias": 1.0}  # Biased to perform well
]

games_per_year = 100  # Number of games in a year
current_year = 1920   # Start year
current_year_games = []  # List to store games for the current year
all_years_data = {}  # Dictionary to store games by year

# Helper function to generate random scores with bias
def generate_score(team_bias):
    base_score = randint(0, 30)
    bias_factor = team_bias + uniform(-0.2, 0.2)  # Small randomness
    return max(0, int(base_score * bias_factor))

# Helper function to simulate a game
def simulate_game(team1, team2):
    score1 = generate_score(team1["bias"])
    score2 = generate_score(team2["bias"])
    return {
        "team1": team1["name"],
        "team2": team2["name"],
        "score1": score1,
        "score2": score2,
        "winner": team1["name"] if score1 > score2 else team2["name"]
    }

# Simulate games every 1 minute
async def game_simulation():
    global current_year, current_year_games
    while True:
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                game = simulate_game(teams[i], teams[j])
                current_year_games.append(game)

                # Check if we've reached the end of the year
                if len(current_year_games) >= games_per_year:
                    # Store current year games in all_years_data
                    all_years_data[current_year] = current_year_games
                    current_year += 1  # Increment the year
                    current_year_games = []  # Reset for the new year

        await asyncio.sleep(60)  # 1 minute

# Start the simulation in the background
@app.on_event("startup")
async def start_simulation():
    asyncio.create_task(game_simulation())

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the NFL Simulation API!"}

@app.get("/teams")
async def get_teams():
    return {"teams": teams}

@app.get("/games/current-year")
async def get_current_year_games():
    return {"year": current_year, "games": current_year_games}

@app.get("/games/all")
async def get_all_years_data():
    return {"all_years_data": all_years_data}

@app.get("/games/{year}")
async def get_games_by_year(year: int):
    if year in all_years_data:
        return {"year": year, "games": all_years_data[year]}
    return {"error": f"No data found for the year {year}"}

@app.post("/simulate-once")
async def simulate_once():
    global current_year, current_year_games
    # Simulate a single round of games
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            game = simulate_game(teams[i], teams[j])
            current_year_games.append(game)

            # Check if we've reached the end of the year
            if len(current_year_games) >= games_per_year:
                # Store current year games in all_years_data
                all_years_data[current_year] = current_year_games
                current_year += 1  # Increment the year
                current_year_games = []  # Reset for the new year

    return {"message": f"Simulated one round of games for year {current_year}.", "games": current_year_games}

@app.post("/clear-data")
async def clear_data():
    global current_year, current_year_games, all_years_data
    # Reset all data
    current_year = 1920
    current_year_games = []
    all_years_data = {}
    return {"message": "All data has been cleared."}
