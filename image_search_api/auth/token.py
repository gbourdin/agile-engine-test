from dataclasses import dataclass, field
from typing import Dict

import requests
from image_search_api.settings.default import API_KEY

from .exceptions import Unauthorized

AUTH_URL: str = "http://interview.agileengine.com/auth"


@dataclass()
class Token:
    """
    Represents an auth token for the agileengine backend. Fetches the token on
     initialization and exposes a method to refresh it should it become invalid
    """

    token: str
    auth: bool
    api_key: str = field(repr=False, default=API_KEY)

    def __init__(self) -> None:
        self.refresh_token()

    def refresh_token(self) -> None:
        """
        Updates the stored api token as it might be expired (or you are
        creating it for the first time) should the api key be invalid or your
        request be rejected by the auth endpoint, an unauthorized exception
        will be raised.
        """
        payload: Dict[str, str] = {"apiKey": API_KEY}
        headers: Dict[str, str] = {"Content-Type": "application/json"}

        r: requests.Response = requests.post(AUTH_URL, json=payload, headers=headers)

        if r.status_code != 200:
            raise Unauthorized(msg="Bad response from server")

        response = r.json()
        token: str = response.get("token") or ""
        auth: bool = response.get("auth", False)

        if not auth or not token:
            raise Unauthorized(msg="Bad response from server")

        self.token = token
        self.auth = auth
