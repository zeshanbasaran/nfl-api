from fastapi import FastAPI
from random import randint, uniform
import asyncio
import json
from pathlib import Path

app = FastAPI()

# Initialize data
teams = [
    {"id": 1, "name": "Team 1", "bias": 0.3},  # Biased to perform badly
    {"id": 2, "name": "Team 2", "bias": 0.8},
    {"id": 3, "name": "Team 3", "bias": 0.1},
    {"id": 4, "name": "Team 4", "bias": 0.2},
    {"id": 5, "name": "Team 5", "bias": 1.0},
    {"id": 6, "name": "Team 6", "bias": 0.7},
    {"id": 7, "name": "Team 7", "bias": 0.4},
    {"id": 8, "name": "Team 8", "bias": 0.9},
    {"id": 9, "name": "Team 9", "bias": 0.5},
    {"id": 10, "name": "Team 10", "bias": 0.6}  # Biased to perform well
]

games = []  # Store past games
MAX_GAMES = 1000
GAMES_FILE = "games.json"

# Helper functions to save/load games to/from a JSON file
def save_to_file(data, filename=GAMES_FILE):
    with open(filename, "w") as f:
        json.dump(data, f)

def load_from_file(filename=GAMES_FILE):
    if Path(filename).exists():
        with open(filename, "r") as f:
            return json.load(f)
    return []

# Load games on startup
games = load_from_file()

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
    while True:
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                game = simulate_game(teams[i], teams[j])
                games.append(game)
                if len(games) > MAX_GAMES:
                    games.pop(0)  # Keep the list size to MAX_GAMES
        save_to_file(games)  # Save games to JSON after each round
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

@app.get("/games")
async def get_games():
    return {"games": games}

@app.get("/simulate-once")
async def simulate_once():
    # Simulate a single round of games
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            game = simulate_game(teams[i], teams[j])
            games.append(game)
            if len(games) > MAX_GAMES:
                games.pop(0)
    save_to_file(games)  # Save games to JSON
    return {"message": "Simulated one round of games.", "games": games}

@app.get("/team-stats")
async def get_team_stats():
    team_stats = {team["name"]: {"wins": 0, "losses": 0} for team in teams}
    
    for game in games:
        winner = game["winner"]
        team_stats[winner]["wins"] += 1
        
        loser = game["team1"] if game["team1"] != winner else game["team2"]
        team_stats[loser]["losses"] += 1
    
    return team_stats

