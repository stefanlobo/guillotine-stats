import os
import json
import requests
import glob
from pathlib import Path

from utils import save_to_json, load_json

from dotenv import load_dotenv


def get_weekly_matchups(league_id, week):
    """
    Fetch weekly matchups from Sleeper API.

    :param league_id: The ID of the fantasy league
    :param week: The week number for which to fetch matchups
    :return: A list of matchup data for the specified week
    """
    # Endpoint to get the matchup data for a specific week
    url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"

    try:
        # Sending the GET request to Sleeper API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching matchups: {e}")
        return None


def get_league_rosters(league_id):
    """Fetch the rosters for the specified league."""
    url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}


def get_user_info(user_id):
    """Fetch user info for the given user ID."""
    url = f"https://api.sleeper.app/v1/user/{user_id}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}


def associate_rosters_with_users(league_id):
    """Associates roster IDs with user information."""
    rosters = get_league_rosters(league_id)

    roster_user_map = {}
    for roster_data in rosters:
        user_id = roster_data["owner_id"]  # Assuming 'owner_id' is the key for user ID
        user_info = get_user_info(user_id)

        # Skip the bot account
        if user_info["display_name"] == "GLExecutioner":
            continue
        else:
            # Store roster ID and user information
            roster_user_map[roster_data["roster_id"]] = {
                #'user_id': user_id,
                # "user_info": user_info
                "username": user_info["display_name"]
            }

    return roster_user_map


def update_weekly_matchups(year_map):
    for week in range(1, 19):
        matchups = get_weekly_matchups(year_map[year], week)
        # Write JSON data to a file
        file_path = f"{year}/week_{week}.json"
        save_to_json(matchups, file_path)


def death_week(roster) -> list:
    # Create a list of tuples (user_name, user_data)
    user_list = [(user, data) for user, data in roster.items()]

    # Sort the list by 'death_week' (which is in the second item of the tuple)
    sorted_users = sorted(
        user_list, key=lambda x: (x[1]["death_week"] is None, x[1]["death_week"])
    )

    # Print the sorted list
    for user, data in sorted_users:
        print(f"{user}: death_week is {data['death_week']}")

    return sorted_users


def calculate_death_week(scores):
    """Helper function to determine the last week with a non-zero score."""
    for week in reversed(range(len(scores))):
        if scores[week] > 0:
            return week + 1  # Convert 0-indexed week to 1-indexed
    return None  # All scores were 0


def scores(year, player_info, roster_association):
    # Step 1: Find all week JSON files
    week_files = glob.glob(f"{year}/week_*.json")

    # Step 2: Sort the files based on week number
    # This sorts based on the numeric part of the filename
    sorted_week_files = sorted(
        week_files, key=lambda x: int(x.split("_")[1].split(".")[0])
    )

    # Step 3: Load JSON data from sorted files
    for week_file in sorted_week_files:
        week_data = load_json(week_file)
        week_number = week_file.split("_")[1].split(".")[0]

        # Update user data with scores for the current week
        for matchup in week_data:
            roster_id = matchup["roster_id"]
            if roster_id in roster_association:
                username = roster_association[roster_id]["username"]
                score = matchup["points"]

                # Append the score to the user's scores list
                player_info[username]["scores"].append(score)

    # Calc death week
    for username, data in player_info.items():
        data["death_week"] = calculate_death_week(data["scores"])

    return player_info


def user_info_init(roster_association):
    player_info = {}

    # Initialize user data from the roster association
    for roster_id, user_info in roster_association.items():
        username = user_info["username"]
        player_info[username] = {"scores": [], "death_week": None}

    return player_info


def death_week(roster) -> list:
    # Create a list of tuples (user_name, user_data)
    user_list = [(user, data) for user, data in roster.items()]

    # Sort the list by 'death_week' (which is in the second item of the tuple)
    sorted_users = sorted(
        user_list, key=lambda x: (x[1]["death_week"] is None, x[1]["death_week"])
    )

    # Print the sorted list
    for user, data in sorted_users:
        print(f"{user}: death_week is {data['death_week']}")

    return sorted_users


def champion(users):
    last_one_user, last_one_user_data = users[-1]
    last_two_user, last_two_user_data = users[-2]

    if last_one_user_data["scores"][-1] > last_two_user_data["scores"][-1]:
        print("Champion: ", last_one_user)
        champion_name = last_one_user
    else:
        print("Champion: ", last_two_user)
        champion_name = last_two_user

    return champion_name


def update_info(roster, champion):
    # Update the death_week of the champion to None (equivalent to null in JSON)
    roster[champion]["death_week"] = None
    save_to_json(roster, f"{year}/sleeper_user_info.json")


if __name__ == "__main__":
    load_dotenv("website.env")

    year_map = json.loads(os.getenv("YEAR_MAP"))  # league ID hash map

    for year in year_map.keys():
        # Create the directory if it doesn't exist
        Path(year).mkdir(parents=True, exist_ok=True)
        print(f"Directory '{year}' created or already exists.")

        roster_user_association = associate_rosters_with_users(year_map[year])

        # Save the roster-user association to a JSON file
        output_filename = f"{year}/roster_user_association_{year}.json"
        save_to_json(roster_user_association, output_filename)

        # Fills in the user info json that has the user, their scores and their death week
        players = user_info_init(roster_user_association)
        players_full = scores(year, players, roster_user_association)
        output_filename = f"{year}/sleeper_user_info.json"
        save_to_json(players_full, output_filename)

        sorted_by_death = death_week(players_full)
        champion_name = champion(sorted_by_death)
        update_info(players_full, champion_name)

    # week = 1  # Replace with the week number you want to query

    # Get the weekly matchups
    # matchups = get_weekly_matchups(league_id, week)

    # if matchups:
    #     # Print each matchup's details
    #     for matchup in matchups:
    #         print(f"Matchup ID: {matchup['matchup_id']}")
    #         print(f"Roster ID: {matchup['roster_id']}")
    #         print(f"Starters: {matchup['starters']}")
    #         print(f"Players: {matchup['players']}")
    #         print(f"Points: {matchup['points']}")
    #         print("-" * 30)
