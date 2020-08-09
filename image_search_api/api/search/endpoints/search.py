import logging
from datetime import datetime
from typing import List

from image_search_api.models.pictures import Picture

from flask import current_app as app
from flask_restx import Namespace, Resource, fields

logger = logging.getLogger(__name__)

search_ns = Namespace("search", description="Image Search API")
cache_ns = Namespace("cache", description="Cache Updater")


ImageModel = search_ns.model(
    "Image",
    {
        "id": fields.String(),
        "author": fields.String(),
        "camera": fields.String(),
        "tags": fields.String(),
        "cropped_picture": fields.String(),
        "full_picture": fields.String(),
    },
)

Model = search_ns.model("results", {"results": fields.List(fields.Nested(ImageModel))})


@search_ns.route("/<query>")
class Search(Resource):
    @search_ns.marshal_with(Model, code=200, description="Image Search API")
    def get(self, query: str):
        """
        Search for images matching the request querystring
        """

        start = datetime.now()

        # Get matching pictures
        pictures: List[Picture] = app.pictures_cache.search(query=query)
        duration_msec = (datetime.now() - start).total_seconds() * 1000

        app.logger.info(
            "Search result for: {} returned: {} results and took {} msec".format(
                query, len(pictures), duration_msec
            )
        )

        results = {"results": [image.to_dict() for image in pictures]}
        return results, 200


@cache_ns.route("/update_cache")
class UpdateCache(Resource):
    def get(self):
        """
        Forces a cache update. Internal endpoint to be used by
        scheduled worker
        """
        start = datetime.now()
        app.logger.info("Updating cached images...")

        app.pictures_cache.update_cache()

        duration_msec = (datetime.now() - start).total_seconds() * 1000
        app.logger.info("Cache updated. Took {} msec".format(duration_msec))

        return "success", 200
