from typing import Dict
import requests

from image_search_api.auth.token import Token
from image_search_api.auth.exceptions import Unauthorized


def get_headers(token: str) -> Dict[str, str]:
    """
    Simple helper to build api call headers
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }
    return headers


def request_and_retry_with_token_update(
    token: Token, url: str, retries: int = 1, **kwargs
) -> requests.Response:

    """
    Handles retrying a request should it fail for any reason, main focus
    is on retrying because of an expired API token.

    Will try to provide a successful response up to `retries` times, if not
    possible, returns the error for the user to handle.
    """

    headers = get_headers(token.token)

    try:
        r = requests.get(url, headers=headers, **kwargs)
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        if retries > 0:  # I'll handle it
            try:
                token.refresh_token()
            except Unauthorized:
                # Token is broken, cant fix
                return r

            return request_and_retry_with_token_update(
                token=token, url=url, retries=retries - 1, **kwargs
            )

    return r  # User must handle response
