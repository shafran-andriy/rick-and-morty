import time

import requests
from requests import Response

from characters.models import Character
from rick_and_morty_api import settings


def _get_json_response(url: str, retries: int = 5) -> dict:
    for attempt in range(retries):
        response: Response = requests.get(url, timeout=15)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else 2 * (attempt + 1)
            time.sleep(wait_seconds)
            continue

        response.raise_for_status()

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as exc:
            content_type = response.headers.get("content-type", "unknown")
            body_preview = response.text[:200].strip() or "<empty body>"
            raise ValueError(
                f"Rick and Morty API returned non-JSON content for {url}. "
                f"status={response.status_code}, content-type={content_type}, body={body_preview!r}"
            ) from exc

    raise ValueError(f"Rick and Morty API rate limit persisted after {retries} retries for {url}")


def scrape_characters() -> list[Character]:
    next_url_to_scrape = settings.RICK_AND_MORTY_API_CHARACTERS_URL
    characters = []

    while next_url_to_scrape is not None:
        characters_response = _get_json_response(next_url_to_scrape)

        for character_dict in characters_response["results"]:
            characters.append(
                Character(
                    api_id=character_dict["id"],
                    name=character_dict["name"],
                    status=character_dict["status"],
                    species=character_dict["species"],
                    gender=character_dict["gender"],
                    image=character_dict["image"],
                )
            )

        next_url_to_scrape = characters_response["info"]["next"]
        time.sleep(0.5)

    return characters


def save_characters(characters: list[Character]) -> None:
    for character in characters:
        Character.objects.update_or_create(
            api_id=character.api_id,
            defaults={
                "name": character.name,
                "status": character.status,
                "species": character.species,
                "gender": character.gender,
                "image": character.image,
            },
        )


def sync_characters_with_api() -> None:
    characters = scrape_characters()
    save_characters(characters)
