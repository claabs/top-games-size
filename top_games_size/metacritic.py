import datetime

import requests


def get_top_rated_games_metacritic(platform, **kwargs):
    limit = kwargs.get("limit")
    use_critic_ratings = kwargs.get("use_critic_ratings")

    offset = 0
    all_game_titles = []

    while len(all_game_titles) < limit:
        params = {
            "sortBy": "-metaScore" if use_critic_ratings else "-userScore",
            "productType": "games",
            "gamePlatformIds": platform.metacritic_id,
            "releaseYearMin": 1958,
            "releaseYearMax": datetime.date.today().year,
            "limit": min(
                50, limit - len(all_game_titles)
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
            game_titles = [game.get("title") for game in games]
            all_game_titles.extend(game_titles)

            # Increment offset for next batch
            offset += len(games)

            # Break the loop if no more games available or limit reached
            if len(games) < 50 or len(all_game_titles) >= limit:
                break
        else:
            # Handle unsuccessful response
            print(f"Request failed with status code {response.status_code}")
            break

    return all_game_titles[:limit]  # Truncate to the specified limit
