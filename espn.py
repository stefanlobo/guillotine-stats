# Football API
from espn_api.football import League

import requests
from pathlib import Path

from utils import save_to_json, load_json

from dotenv import load_dotenv
import os


def user_info(league) -> dict:
    roster_user_map = {}

    for x in range(len(league.teams)):
        team = league.teams[x]
        owners = team.owners
        full_name = owners[0]["firstName"] + " " + owners[0]["lastName"]
        total_weeks = len(team.scores)
        min_week = [0] * total_weeks

        scores = team.scores
        x, y = 0, 1
        while y < total_weeks and scores[y] != 0:
            y += 1

        x = y - 1
        min_week[x] = scores[x]

        roster_user_map[full_name] = {"scores": scores, "death_week": y}

    return roster_user_map


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


def retrieve_info_espn(league):
    # Retrieves info regarding every member
    save_to_json(league.members, f"{year}/members")

    # Retrieves info regarding every user
    roster_info = user_info(league)
    save_to_json(roster_info, f"{year}/espn_user_info.json")


def update_info(roster, champion):
    # Update the death_week of the champion to None (equivalent to null in JSON)
    roster[champion]["death_week"] = None
    save_to_json(roster, f"{year}/espn_user_info.json")


if __name__ == "__main__":

    load_dotenv("website.env")
    league_id = os.getenv("ESPN_LEAGUE_ID")
    espn_s2 = os.getenv("ESPN_S2")
    swid = os.getenv("ESPN_SWID")

    league = League(league_id=league_id, year=2022, espn_s2=espn_s2, swid=swid)

    # print(len(matchups))
    # print(matchups)
    # print(matchups[0].away_score)

    for year in range(2019, 2023):
        # Create the directory if it doesn't exist
        Path(str(year)).mkdir(parents=True, exist_ok=True)
        print(f"Directory '{year}' created or already exists.")

        # league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

        roster_path = f"{year}/espn_user_info.json"

        roster_info_retieval = load_json(roster_path)

        user_sorted = death_week(roster_info_retieval)

        champion_name = champion(user_sorted)

        update_info(roster_info_retieval, champion_name)
