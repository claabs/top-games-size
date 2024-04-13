import os

import requests
from dotenv import load_dotenv
from igdb.igdbapi_pb2 import GameResult, PlatformResult
from igdb.wrapper import IGDBWrapper

load_dotenv()

wrapper = None


def get_wrapper():
    params = {
        "client_id": os.getenv("IGDB_CLIENT_ID"),
        "client_secret": os.getenv("IGDB_CLIENT_SECRET"),
        "grant_type": "client_credentials",
    }

    # Send POST request to the API endpoint
    response = requests.post("https://id.twitch.tv/oauth2/token", params=params)

    # Check if request was successful
    if response.status_code == 200:
        # Parse response JSON
        data = response.json()
        access_token = data.get("access_token")
        wrapper = IGDBWrapper(os.getenv("IGDB_CLIENT_ID"), access_token)
        return wrapper

    else:
        print("Error:", response.text)


def get_top_rated_games(platform, **kwargs):
    limit = platform.limit
    min_ratings = kwargs.get("min_ratings")
    use_critic_ratings = kwargs.get("use_critic_ratings")

    global wrapper
    if not wrapper:
        wrapper = get_wrapper()

    # Protobuf API request

    rating_query = (
        f"aggregated_rating_count >= {min_ratings} ; sort aggregated_rating desc;"
        if use_critic_ratings
        else f"rating_count >= {min_ratings} ; sort rating desc;"
    )
    byte_array = wrapper.api_request(
        "games.pb",  # Note the '.pb' suffix at the endpoint
        f"fields name; offset 0; where platforms={platform.igdb_id} & {rating_query} limit {limit};",
    )
    games_message = GameResult()
    games_message.ParseFromString(
        byte_array
    )  # Fills the protobuf message object with the response
    games = games_message.games

    return list(map(lambda x: x.name, games))


def get_platforms():
    global wrapper
    if not wrapper:
        wrapper = get_wrapper()

    # Protobuf API request

    byte_array = wrapper.api_request(
        "platforms.pb",  # Note the '.pb' suffix at the endpoint
        "fields name, id; offset 0; sort id asc; limit 500;",
    )
    platform_message = PlatformResult()
    platform_message.ParseFromString(
        byte_array
    )  # Fills the protobuf message object with the response
    platforms = platform_message.platforms
    for platform in platforms:
        print(f"{platform.id}: {platform.name}")
    return platforms
