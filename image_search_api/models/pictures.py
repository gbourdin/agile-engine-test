import tqdm
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple

from image_search_api.auth.token import Token
from image_search_api.models.request_utils import request_and_retry_with_token_update
from image_search_api.models.string_utils import get_tokens, get_tokens_for_tags

from collections import Counter


PICTURES_API_BASE_URL: str = "http://interview.agileengine.com/images"
PICTURE_DETAILS_URL: str = "http://interview.agileengine.com/images/{image_id}"


@dataclass
class Picture:
    id: str
    cropped_picture: str
    full_picture: str
    author: str = ""
    camera: str = ""
    tags: str = ""

    @classmethod
    def from_api(cls, picture_id: str, token: Token):

        url = PICTURE_DETAILS_URL.format(image_id=picture_id)
        r = request_and_retry_with_token_update(token=token, url=url, retries=1)

        if r.status_code != 200:
            # Image does not exist, or toke is invalid, can't fetch
            return None

        return cls.from_dict(r.json())

    @classmethod
    def from_dict(cls, api_response: Dict):
        """
        Build an image from api response, skip any unknown fields
        """
        field_names = [
            "id",
            "author",
            "camera",
            "tags",
            "cropped_picture",
            "full_picture",
        ]

        values = {k: v for k, v in api_response.items() if k in field_names}

        return Picture(**values)

    def to_dict(self) -> Dict:
        return asdict(self)


class PicturesCache:

    SEARCH_FIELDS = {
        "author": {
            "field_name": "author",
            "index_name": "author",
            "tokenizer": get_tokens,
        },
        "camera": {
            "field_name": "camera",
            "index_name": "camera",
            "tokenizer": get_tokens,
        },
        "tags": {
            "field_name": "tags",
            "index_name": "tags",
            "tokenizer": get_tokens_for_tags,
        },
    }

    def __init__(self):
        self.cached_pictures = {}
        self.indexes = {"author": {}, "camera": {}, "tags": {}}

    def update_cache(self):
        """
        Gets all the picture_ids that need to be downloaded and queues the
        download task
        """
        token: Token = Token()
        picture_ids: Set[str] = set(self._get_all_picture_ids_from_api(token))
        cached_ids: Set[str] = set(self.cached_pictures.keys())

        pictures_to_download = picture_ids - cached_ids
        pictures_to_delete = cached_ids - picture_ids

        if (not pictures_to_download) and (not pictures_to_delete):
            # No downloads or re-indexing necessary
            return

        for picture_id in pictures_to_delete:  # Clear stale cached pictures
            self.cached_pictures.pop(picture_id)

        # Download new pictures and add them to cache
        print("Downloading pictures")
        for picture_id in tqdm.tqdm(pictures_to_download):
            picture = Picture.from_api(picture_id, token)
            self.cached_pictures[picture_id] = picture

        self.update_indexes()

    @staticmethod
    def _get_all_picture_ids_from_api(token: Token) -> List[str]:
        current_page: int = 1
        total_pages: int = 1
        has_more: bool = True
        picture_ids: List[str] = []

        while has_more:
            print(
                "Getting picture ids. Fetching page {} out of {}".format(
                    current_page, total_pages
                )
            )

            params = {"page": current_page}
            r = request_and_retry_with_token_update(
                token, url=PICTURES_API_BASE_URL, params=params
            )

            if r.status_code != 200:
                break  # Request failed, wait for next cache update

            response = r.json()

            pictures = response.get("pictures", [])
            for picture in pictures:
                picture_ids.append(picture.get("id"))

            total_pages = response.get("pageCount", 1)
            current_page = response.get("page", 1) + 1
            # has_more = response.get("hasMore") and current_page <= total_pages
            has_more = response.get("hasMore") and current_page <= 2

        return picture_ids

    def update_indexes(self) -> None:
        """
        Drop existing indexes and build new ones for cached images
        :return:
        """
        for index_name in ["author", "camera", "tags"]:
            self.indexes[index_name] = {}  # Just an empty dict

        for picture in self.cached_pictures.values():
            self.index_picture(picture)

    def index_picture(self, picture: Picture) -> None:
        """
        Adds tokens for this picture to all the available search indexes
        """

        for field in self.SEARCH_FIELDS.values():
            tokenizer = field["tokenizer"]
            field_value = getattr(picture, field["field_name"])
            tokens = tokenizer(field_value)
            self.add_picture_tokens_to_index(field["index_name"], picture.id, tokens)

    def add_picture_tokens_to_index(
        self, index_name: str, picture_id: str, tokens: List[str]
    ) -> None:
        """
        Adds the tokens for a picture to the matching tokens list for
        a particular index. If no list existed, it is created
        """
        index = self.indexes[index_name]
        for token in tokens:
            indexed_pictures = index.get(token, [])
            indexed_pictures.append(picture_id)
            index[token] = indexed_pictures

    def search(self, query: str, field: Optional[str] = None) -> List[Picture]:
        """
        Given a valid field name and a value to search, returns a list of
        pictures that match the criteria.
        If field is invalid or no field is provided, results will be matched
        against all fields.
        Results are ordered from best to worst match.
        """
        if field not in self.SEARCH_FIELDS or not field:
            fields = self.SEARCH_FIELDS.keys()
        else:
            fields = [field]

        results = self._get_results_for_fields(query, fields)

        return results

    def _get_results_for_fields(self, query: str, fields: List[str]) -> List[Picture]:
        """
        Internal usage, looks for the search term in all the provided fields
        ranks results by popularity and number of appearences
        """
        results: List[Picture] = []
        picture_ids: List[str] = []

        for field in fields:
            index_name = self.SEARCH_FIELDS[field]["index_name"]
            tokenizer = self.SEARCH_FIELDS[field]["tokenizer"]

            index = self.indexes[index_name]
            tokens = tokenizer(query)

            for token in tokens:
                picture_ids += index.get(token, [])

        # Rank by popularity (full matches will match more tokens than partials)
        ranked_pictures: List[Tuple[str, int]] = Counter(picture_ids).most_common()

        for picture_id, rank in ranked_pictures:
            results.append(self.cached_pictures[picture_id])

        return results
