import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch
from anilist_api import get_popular_animes, fetch_data

# Testando fetch_data com mock da requisição HTTP
@patch("anilist_api.requests.post")
def test_fetch_data_returns_list(mock_post):
    mock_post.return_value.json.return_value = {
        "data": {
            "Page": {
                "media": [
                    {"id": 1, "title": {"romaji": "Test Anime"}, "coverImage": {"large": "url"}}
                ]
            }
        }
    }
    mock_post.return_value.raise_for_status.return_value = None

    result = fetch_data("FAKE QUERY")
    assert isinstance(result, list)
    assert result[0]["id"] == 1


# Testando get_popular_animes validando chamada ao fetch_data
@patch("anilist_api.fetch_data")
def test_get_popular_animes(mock_fetch):
    mock_fetch.return_value = [{"id": 123, "title": {"romaji": "Anime X"}}]

    result = get_popular_animes()
    assert result[0]["id"] == 123
    mock_fetch.assert_called_once()
