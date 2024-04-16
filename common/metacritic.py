import datetime
import re
from dataclasses import dataclass
from typing import List

import requests
from joblib import Memory

from top_games_size.platform import Platform

memory = Memory("metacritic_cache")

max_attempts = 3
default_timeout = 15


@memory.cache(ignore=["attempt"])
def cached_get(url, params, attempt=1):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=default_timeout,
        )
        return response
    except Exception as e:
        if attempt > max_attempts:
            raise e
        return cached_get(url, params, attempt=attempt + 1)


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
        response = cached_get(
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


def get_all_game_slugs_metacritic(platforms: List[Platform]):
    offset = 0
    all_games = []
    request_limit = 50

    platform_ids = ",".join(list(map(lambda x: str(x.metacritic_id), platforms)))

    while True:
        params = {
            "sortBy": "-releaseDate",
            "productType": "games",
            "gamePlatformIds": platform_ids,
            "releaseYearMin": 1958,
            "releaseYearMax": datetime.date.today().year,
            "limit": request_limit,
            "apiKey": "1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u",
            "offset": offset,
        }

        print(f"getting offset {offset}")
        # Send GET request to the API endpoint
        response = cached_get(
            "https://internal-prod.apigee.fandom.net/v1/xapi/finder/metacritic/web",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        games = data.get("data", {}).get("items", [])
        game_slugs = list(map(lambda x: x.get("slug"), games))
        all_games.extend(game_slugs)

        offset += len(games)

        # Break the loop if no more games available or limit reached
        if len(games) < request_limit:
            break
    return all_games


@dataclass
class Score:
    score: float
    review_count: int


def get_game_score(game_slug, platform_slug=None, use_critic_ratings=False) -> Score:
    # https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/user/games/ys-viii-lacrimosa-of-dana/platform/playstation-vita/stats/web?apiKey=1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u
    params = {
        "apiKey": "1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u",
    }

    review_author = "critic" if use_critic_ratings else "user"
    platform = f"/platform/{platform_slug}" if platform_slug else ""
    response = cached_get(
        f"https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/{review_author}/games/{game_slug}{platform}/stats/web",
        params=params,
    )
    try:
        response.raise_for_status()
    except Exception:
        response = cached_get.call(
            f"https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/{review_author}/games/{game_slug}{platform}/stats/web",
            params=params,
        )
        response.raise_for_status()

    data = response.json()
    item = data.get("data", {}).get("item", {})
    score = item.get("score", None)
    review_count = item.get("reviewCount", 0)

    if review_count is None:
        review_count = 0

    if review_count < 4:
        score = None

    if score and use_critic_ratings:
        score = score / 10

    return Score(score, review_count)


def get_platform_slug(platform) -> str | None:
    url = platform.get("criticScoreSummary", {}).get("url", "")
    match = re.search(r"\?platform=(.+)", url)
    if match:
        return match.group(1)
    else:
        return None


@dataclass
class ScorePair:
    user_score: Score
    critic_score: Score


@dataclass
class PlatformScorePair(ScorePair):
    platform_slug: str


@dataclass
class GameRatings:
    title: str
    game_slug: str
    overall_score: ScorePair
    platform_scores: List[PlatformScorePair]
    developer: str | None
    publisher: str | None


def get_all_game_ratings(game_slug) -> GameRatings:
    # Get platform slugs
    # https://internal-prod.apigee.fandom.net/v1/xapi/composer/metacritic/pages/games/ys-viii-lacrimosa-of-dana/web?=&apiKey=1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u
    params = {
        "apiKey": "1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u",
    }
    response = cached_get(
        f"https://internal-prod.apigee.fandom.net/v1/xapi/composer/metacritic/pages/games/{game_slug}/web",
        params=params,
    )
    try:
        response.raise_for_status()
    except Exception:
        response = cached_get.call(
            f"https://internal-prod.apigee.fandom.net/v1/xapi/composer/metacritic/pages/games/{game_slug}/web",
            params=params,
        )
        response.raise_for_status()

    data = response.json()
    product = next(
        filter(
            lambda x: x.get("meta", {}).get("componentName", None) == "product",
            data.get("components", []),
        ),
        None,
    )
    if not product:
        raise KeyError(f"Could not find product for {game_slug}")

    product_item = product.get("data", {}).get("item", {})
    platforms = product_item.get("platforms", [])
    platform_slugs = list(map(get_platform_slug, platforms))
    title = product_item.get("title")

    companies = product_item.get("production", {}).get("companies", [])
    developer = next(
        filter(
            lambda x: x.get("typeName") == "Developer",
            companies,
        ),
        None,
    )
    developer = developer.get("name", None) if developer else None
    publisher = next(
        filter(
            lambda x: x.get("typeName") == "Publisher",
            companies,
        ),
        None,
    )
    publisher = publisher.get("name", None) if publisher else None

    platform_scores: List[PlatformScorePair] = []
    for platform_slug in platform_slugs:
        user_score = get_game_score(game_slug, platform_slug, use_critic_ratings=False)
        critic_score = get_game_score(game_slug, platform_slug, use_critic_ratings=True)
        platform_scores.append(
            PlatformScorePair(user_score, critic_score, platform_slug)
        )
    overall_user_score = get_game_score(game_slug, use_critic_ratings=False)
    overall_critic_score = get_game_score(game_slug, use_critic_ratings=True)
    overall_score = ScorePair(overall_user_score, overall_critic_score)
    return GameRatings(
        title, game_slug, overall_score, platform_scores, developer, publisher
    )
