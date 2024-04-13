import datetime

import requests


def get_top_rated_games_metacritic(platform, **kwargs):
    limit = platform.limit
    use_critic_ratings = kwargs.get("use_critic_ratings")
    min_rating = kwargs.get("min_rating")

    offset = 0
    all_games = []

    while len(all_games) < limit:
        params = {
            "sortBy": "-metaScore" if use_critic_ratings else "-userScore",
            "productType": "games",
            "gamePlatformIds": platform.metacritic_id,
            "releaseYearMin": 1958,
            "releaseYearMax": datetime.date.today().year,
            "limit": min(
                50, limit - len(all_games)
            ),  # Fetching up to 50 records or remaining to reach limit
            "apiKey": "1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u",
            "offset": offset,
        }

        # Send GET request to the API endpoint
        response = requests.get(
            "https://internal-prod.apigee.fandom.net/v1/xapi/finder/metacritic/web",
            params=params,
        )

        # Check if request was successful
        if response.status_code == 200:
            # Parse response JSON
            data = response.json()
            games = data.get("data", {}).get("items", [])
            all_games.extend(games)

            # Increment offset for next batch
            offset += len(games)

            # Break the loop if no more games available or limit reached
            if len(games) < 50 or len(all_games) >= limit:
                break
        else:
            # Handle unsuccessful response
            print(f"Request failed with status code {response.status_code}")
            break

    valid_games = list(
        filter(
            lambda x: x.get("criticScoreSummary").get("score") > min_rating,
            all_games[:limit],
        )
    )
    valid_game_titles = list(map(lambda x: x.get("title"), valid_games))

    return valid_game_titles  # Truncate to the specified limit
