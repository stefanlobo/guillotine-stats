from pathlib import Path
from utils import load_json, save_to_json


def load_year(year):
    year_path = Path(year)
    file_name = ["espn_user_info.json", "sleeper_user_info.json"]

    if year_path.is_dir():  # Check if it's a directory
        # Look for the JSON files in the directory
        for json_file in year_path.iterdir():
            print(json_file.name)
            if json_file.name in file_name:
                try:
                    # Load the JSON data
                    data = load_json(json_file)
                except Exception as e:
                    print(
                        f"Failed to load {json_file.name} for year {year_path.name}: {e}"
                    )

    return data


def calculate_avg_death_week(data):
    """Calculate the average death week for each user, replacing None with the max death week from their scores."""
    for user, user_data in data.items():
        total_weeks = 0
        week_count = 0

        for year, year_data in user_data.items():
            scores = year_data["scores"]
            death_week = year_data["death_week"]

            # Determine the max death week from the length of the scores
            max_death_week = len(scores)

            # Replace None (if death_week is missing) with the max possible death week for that year
            if death_week is None:
                death_week = max_death_week

            total_weeks += death_week
            week_count += 1

        # Calculate the average death week for the user
        average_death_week = total_weeks / week_count if week_count > 0 else 0
        data[user]["average_death_week"] = average_death_week

    return data


def print_sorted_by_best_death_week(data):
    # Extract the usernames and their average death weeks
    users_with_avg_death_week = [
        (user, user_data["average_death_week"]) for user, user_data in data.items()
    ]

    # Sort by the average death week (lower is better)
    sorted_users = sorted(users_with_avg_death_week, key=lambda x: x[1], reverse=True)

    # Print the sorted usernames and their average death week
    for user, avg_death_week in sorted_users:
        print(f"{user}: Average Death Week = {avg_death_week:.2f}")


if __name__ == "__main__":
    file_name = ["espn_user_info.json", "sleeper_user_info.json"]

    final_player = {}

    espn_to_sleeper_names = load_json("espn_to_sleeper_name_asso.json")

    for year in range(2019, 2024):
        data = load_year(str(year))
        print(data)

        year_key_deaths = f"{year}_death_week"
        year_key_scores = f"{year}_scores"

        for user, info in data.items():
            score_year = info.get("scores", None)
            death_week = info.get("death_week", None)  # None if no death week

            # convert from espn to sleeper
            if user in espn_to_sleeper_names:
                user = espn_to_sleeper_names[user]

            # If user is not already in the dictionary, initialize
            if user not in final_player:
                final_player[user] = {}

            # Store the death week for the corresponding year
            final_player[user][year] = {"scores": score_year, "death_week": death_week}

    final_player = calculate_avg_death_week(final_player)

    # Assuming 'updated_data_with_averages' is your data with average death weeks
    print_sorted_by_best_death_week(final_player)

    save_to_json(final_player, "final_deaths.json")
