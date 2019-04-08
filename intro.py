import json
from flask import Flask

with open("player_results.json", 'r') as player_dict:
    player_results_dict = json.loads(player_dict.read())

total_games_tvp = player_results_dict["Terran"]["Protoss"]["loss"] + player_results_dict["Terran"]["Protoss"]["win"]
win_rate = player_results_dict["Terran"]["Protoss"]["win"] / total_games_tvp
#if win_rate <= 0.5:
    #print("Get good!")


app = Flask(__name__)


@app.route('/')
def get_session_stats():
    return str("TvP :" + str(win_rate)[:4] +"%")
