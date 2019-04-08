import json
import click
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def parse_race_win_loss_result(game_outcome, player_race, opponent_race, win_loss_dict):
    if game_outcome == 1:
        win_loss_dict[player_race][opponent_race]["win"] += 1
    elif game_outcome == 2:
        win_loss_dict[player_race][opponent_race]["loss"] += 1


def parse_replay(replay_json_data, player_to_track):
    with open("player_results.json", 'r') as player_dict:
        win_loss_dict = json.loads(player_dict.read())
    for items in replay_json_data:
        raw_data = json.loads(items)
        if u"m_playerList" in raw_data:
            player_list = raw_data[u"m_playerList"]
            player_to_track_race = None
            game_outcome = None
            opponent_race = None
            for list_data in player_list:
                if u"m_result" in list_data and player_to_track == str(list_data[u"m_name"]):
                    game_outcome = list_data[u"m_result"]
                    player_to_track_race = list_data[u"m_race"]
                elif u"m_result" in list_data and player_to_track != str(list_data[u"m_name"]):
                    opponent_race = list_data[u"m_race"]

            parse_race_win_loss_result(game_outcome, player_to_track_race, opponent_race, win_loss_dict)

    with open("player_results.json", 'w') as player_dict:
        player_dict.write(json.dumps(win_loss_dict, indent=2))


class Handler(FileSystemEventHandler):
    def __init__(self, player_to_track):
        self.player_to_track = player_to_track

    def on_any_event(self, event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            with open(str(event.src_path), 'r') as input_file:
                report_data = input_file.readlines()
            parse_replay(report_data, self.player_to_track)


directory_help_text = "The desired directory to monitor for sc2 replay json output files."
player_to_track_help_text = "The desired StarCraft username to track session stats for!"


@click.command()
@click.option("--directory", "-d", help=directory_help_text,  prompt=directory_help_text, required=True)
@click.option("--player_name_to_track", "-p", help=player_to_track_help_text,  prompt=player_to_track_help_text,
              required=True)
@click.option("--reset_session", "-r", help="Reset player_results.json to 0s")
def sc2_replay_monitor(directory, player_name_to_track, reset_session):
    if reset_session:
        with open("player_results.json", 'r') as player_dict:
            win_loss_dict = json.loads(player_dict.read())
            for item in win_loss_dict["Terran"]:
                win_loss_dict["Terran"][item]["win"] = 0
                win_loss_dict["Terran"][item]["loss"] = 0
            for item in win_loss_dict["Protoss"]:
                win_loss_dict["Protoss"][item]["win"] = 0
                win_loss_dict["Protoss"][item]["loss"] = 0
            for item in win_loss_dict["Zerg"]:
                win_loss_dict["Zerg"][item]["win"] = 0
                win_loss_dict["Zerg"][item]["loss"] = 0
        with open("player_results.json", 'w') as player_dict:
            player_dict.write(json.dumps(win_loss_dict, indent=2))
    player_to_track = str(player_name_to_track)
    logging.info("Starting Session Stats Tracker!")
    path = directory
    event_handler = Handler(player_to_track=player_to_track)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Shutting Down Session Stats Tracker!")
        observer.stop()
    observer.join()

