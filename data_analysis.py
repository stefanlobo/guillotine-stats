from pathlib import Path
from utils import load_json, save_to_json


def load_year(year):
    year_path = Path(year)
    file_name = ["espn_user_info.json", "sleeper_user_info.json"]

    if year_path.is_dir():  # Check if it's a directory
        # Look for the JSON files in the directory
        for json_file in year_path.iterdir():
            # print(json_file.name)
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

def highest_in_year(data):
    highest_scores_per_year = {}

    for year in range(2019, 2024):
        max_score = 0
        top_scorer = None
        top_week = None

        for user, data in final_player.items():
            if year in data:
                scores = data[year]["scores"]
                if scores:
                    # Find the highest score and its corresponding week index
                    user_max_score = max(scores)
                    user_max_week = scores.index(user_max_score) + 1  # +1 to make it 1-indexed

                    # Update if this user has the highest score for the year
                    if user_max_score > max_score:
                        max_score = user_max_score
                        top_scorer = user
                        top_week = user_max_week

        highest_scores_per_year[year] = {
            "player": top_scorer,
            "score": max_score,
            "week": top_week
        }

    return highest_scores_per_year

def lowest_in_year(data):
    lowest_scores_per_year = {}

    for year in range(2019, 2024):
        min_score = float('inf')
        bottom_scorer = None
        bottom_week = None

        for user, data in final_player.items():
            if year in data:
                scores = data[year]["scores"]
                if scores:
                    # Filter out scores of 0 and find the lowest score
                    valid_scores = [score for score in scores if score > 0]

                    if valid_scores:  # Only proceed if there are valid scores
                        user_min_score = min(valid_scores)
                        user_min_week = scores.index(user_min_score) + 1  # +1 to make it 1-indexed

                        # Update if this user has the lowest score for the year
                        if user_min_score < min_score:
                            min_score = user_min_score
                            bottom_scorer = user
                            bottom_week = user_min_week

        lowest_scores_per_year[year] = {
            "player": bottom_scorer,
            "score": min_score,
            "week": bottom_week
        }

    return lowest_scores_per_year

def narrowest_loss(data):
    narrowest_losses_per_year = {}

    for year in range(2019, 2024):
        closest_diff = float('inf')  # Start with a large value
        lowest_score_user = None
        second_lowest_score_user = None
        narrowest_week = None
        narrowest_players = (None, None)

        # Initialize a dictionary to hold weekly scores for each week
        weekly_scores = {week: [] for week in range(1, 19)}  # Assuming 18 weeks max

        # Collect scores for each week from all users
        for user, user_data in data.items():
            if year in user_data:
                scores = user_data[year]["scores"]
                
                # Append each user's score to the corresponding week
                for week, score in enumerate(scores, start=1):
                    if score > 0:  # Only consider scores greater than 0
                        weekly_scores[week].append((score, user))

        # For each week, find the narrowest difference between the lowest two scores
        for week, scores in weekly_scores.items():
            if len(scores) >= 2:  # Only consider weeks with at least two valid scores
                # Sort scores to find the lowest two
                sorted_scores = sorted(scores)  # Sort by score, ascending
                lowest_score, lowest_user = sorted_scores[0]
                second_lowest_score, second_user = sorted_scores[1]

                # Calculate the difference
                diff = second_lowest_score - lowest_score

                # Update if this is the narrowest difference found so far
                if diff < closest_diff:
                    closest_diff = diff
                    narrowest_week = week
                    narrowest_players = (lowest_user, second_user)
                    lowest_score_user = (lowest_user, lowest_score)
                    second_lowest_score_user = (second_user, second_lowest_score)

        # Store the narrowest loss for the year
        if narrowest_week is not None:
            narrowest_losses_per_year[year] = {
                "week": narrowest_week,
                "lowest": lowest_score_user,
                "second lowest":  second_lowest_score_user,
                "difference": closest_diff
            }
    # print(weekly_scores)
    return narrowest_losses_per_year

# Largest difference between lowest and second lowest
def bye_week(data):
    largest_diff_per_year = {}

    for year in range(2019, 2024):
        largest_diff = 0  # Start with a large value
        lowest_score_user = None
        second_lowest_score_user = None
        wide_week = None
        closest_players = (None, None)

        # Initialize a dictionary to hold weekly scores for each week
        weekly_scores = {week: [] for week in range(1, 19)}  # Assuming 18 weeks max

        # Collect scores for each week from all users
        for user, user_data in data.items():
            if year in user_data:
                scores = user_data[year]["scores"]
                
                # Append each user's score to the corresponding week
                for week, score in enumerate(scores, start=1):
                    if score > 0:  # Only consider scores greater than 0
                        weekly_scores[week].append((score, user))

        # For each week, find the difference between the lowest two scores
        for week, scores in weekly_scores.items():
            if len(scores) >= 2:  # Only consider weeks with at least two valid scores
                # Sort scores to find the lowest two
                sorted_scores = sorted(scores)  # Sort by score, ascending
                lowest_score, lowest_user = sorted_scores[0]
                second_lowest_score, second_user = sorted_scores[1]

                # Calculate the difference
                diff = second_lowest_score - lowest_score

                # Update if this is the narrowest difference found so far
                if diff > largest_diff:
                    largest_diff = diff
                    wide_week = week
                    closest_players = (lowest_user, second_user)
                    lowest_score_user = (lowest_user, lowest_score)
                    second_lowest_score_user = (second_user, second_lowest_score)

        # Store the narrowest loss for the year
        if wide_week is not None:
            largest_diff_per_year[year] = {
                "week": wide_week,
                "lowest": lowest_score_user,
                "second lowest":  second_lowest_score_user,
                "difference": largest_diff
            }
    # print(weekly_scores)
    return largest_diff_per_year

# Largest difference between lowest and highest score
def david_goliath(data):
    largest_diff_per_year = {}

    for year in range(2019, 2024):
        largest_diff = 0  # Start with a large value
        lowest_score_user = None
        highest_score_user = None
        wide_week = None
        closest_players = (None, None)

        # Initialize a dictionary to hold weekly scores for each week
        weekly_scores = {week: [] for week in range(1, 19)}  # Assuming 18 weeks max

        # Collect scores for each week from all users
        for user, user_data in data.items():
            if year in user_data:
                scores = user_data[year]["scores"]
                
                # Append each user's score to the corresponding week
                for week, score in enumerate(scores, start=1):
                    if score > 0:  # Only consider scores greater than 0
                        weekly_scores[week].append((score, user))

        # For each week, find the difference between the lowest two scores
        for week, scores in weekly_scores.items():
            if len(scores) >= 2:  # Only consider weeks with at least two valid scores
                # Sort scores to find the lowest two
                sorted_scores = sorted(scores)  # Sort by score, ascending
                lowest_score, lowest_user = sorted_scores[0]
                highest_score, highest_user = sorted_scores[-1]

                # Calculate the difference
                diff = highest_score - lowest_score

                # Update if this is the narrowest difference found so far
                if diff > largest_diff:
                    largest_diff = diff
                    wide_week = week
                    closest_players = (lowest_user, highest_user)
                    lowest_score_user = (lowest_user, lowest_score)
                    highest_score_user = (highest_user, highest_score)

        # Store the narrowest loss for the year
        if wide_week is not None:
            largest_diff_per_year[year] = {
                "week": wide_week,
                "lowest": lowest_score_user,
                "second lowest":  highest_score_user,
                "difference": largest_diff
            }
    # print(weekly_scores)
    return largest_diff_per_year

def top_5_narrowest_losses(data):
    narrowest_losses_per_year = {}

    for year in range(2019, 2024):
        weekly_diffs = []  # To store differences for each week

        # Initialize a dictionary to hold weekly scores for each week
        weekly_scores = {week: [] for week in range(1, 19)}  # Assuming 18 weeks max

        # Collect scores for each week from all users
        for user, user_data in final_player.items():
            if year in user_data:
                scores = user_data[year]["scores"]

                # Append each user's score to the corresponding week
                for week, score in enumerate(scores, start=1):
                    if score > 0:  # Only consider scores greater than 0
                        weekly_scores[week].append((score, user))

        # For each week, find the narrowest difference between the lowest two scores
        for week, scores in weekly_scores.items():
            if len(scores) >= 2:  # Only consider weeks with at least two valid scores
                # Sort scores to find the lowest two
                sorted_scores = sorted(scores)  # Sort by score, ascending
                lowest_score, lowest_user = sorted_scores[0]
                second_lowest_score, second_user = sorted_scores[1]

                # Calculate the difference
                diff = second_lowest_score - lowest_score

                # Append the result for this week
                weekly_diffs.append({
                    "week": week,
                    "players": (lowest_user, second_user),
                    "difference": diff
                })

        # Sort all weekly differences by the smallest difference and select the top 5
        top_5_diffs = sorted(weekly_diffs, key=lambda x: x["difference"])[:5]

        # Store the top 5 narrowest losses for the year
        narrowest_losses_per_year[year] = top_5_diffs

    return narrowest_losses_per_year


if __name__ == "__main__":
    file_name = ["espn_user_info.json", "sleeper_user_info.json"]

    final_player = {}

    espn_to_sleeper_names = load_json("espn_to_sleeper_name_asso.json")

    for year in range(2019, 2024):
        data = load_year(str(year))
        # print(data)

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

    high_scores = highest_in_year(final_player)
    print("Highest Scores by Year:")
    for year, info in high_scores.items():
        print(f"Year: {year}")
        print(f"  Player: {info['player']}")
        print(f"  Score: {info['score']}")
        print(f"  Week: {info['week']}")
        print()  # Adds a blank line for better readability
    
    low_scores = lowest_in_year(final_player)
    print("Lowest Scores by Year:")
    for year, info in low_scores.items():
        print(f"Year: {year}")
        print(f"  Player: {info['player']}")
        print(f"  Score: {info['score']}")
        print(f"  Week: {info['week']}")
        print()  # Adds a blank line for better readability
    
    narrow_lost = narrowest_loss(final_player)
    print("Narrowest Loss by Year:\n")
    for year, info in narrow_lost.items():
        print(f"Year: {year}")
        print(f"  Week: {info['week']}")
        print(f"  Losing Player: {info['lowest']}")
        print(f"  Second Lowest Player: {info['second lowest']}")
        print(f"  Difference: {info['difference']}")
        print()  # Adds a blank line for better readability
    
    top5_narrow = top_5_narrowest_losses(final_player)
    for year, losses in top5_narrow.items():
        print(f"\nTop 5 Narrowest Losses for {year}:\n")
        for i, loss in enumerate(losses, start=1):
            week = loss["week"]
            players = loss["players"]
            difference = loss["difference"]
            print(f"  {i}. Week {week}:")
            print(f"     Players: {players[0]} vs {players[1]}")
            print(f"     Score Difference: {difference:.2f}")
        print("-" * 40)

    largest_gap = bye_week(final_player)
    print("Bye Week Loss by Year:\n")
    for year, info in largest_gap.items():
        print(f"Year: {year}")
        print(f"  Week: {info['week']}")
        print(f"  Losing Player: {info['lowest']}")
        print(f"  Second Lowest Player: {info['second lowest']}")
        print(f"  Difference: {info['difference']}")
        print()  # Adds a blank line for better readability
    
    largest_gap = david_goliath(final_player)
    print("Largest Gap (Highest and Lowest) by Year:\n")
    for year, info in largest_gap.items():
        print(f"Year: {year}")
        print(f"  Week: {info['week']}")
        print(f"  Losing Player: {info['lowest']}")
        print(f"  Second Lowest Player: {info['second lowest']}")
        print(f"  Difference: {info['difference']}")
        print()  # Adds a blank line for better readability
    


    save_to_json(final_player, "final_deaths.json")
