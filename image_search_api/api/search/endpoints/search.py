import logging
from datetime import datetime
from typing import List

from image_search_api.models.pictures import Picture

from flask import current_app as app
from flask_restplus import Namespace, Resource, fields

logger = logging.getLogger(__name__)

ns = Namespace("search", description="Image Search API")


ImageModel = ns.model(
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

Model = ns.model("results", {"results": fields.List(fields.Nested(ImageModel))})


@ns.route("/<query>")
class Predict(Resource):
    @ns.marshal_with(Model, code=200, description="Image Search API")
    def get(self, query: str):
        """
        Search for images matching the request querystring
        """

        start = datetime.now()
        pictures: List[Picture] = app.pictures_cache.search(query=query)
        duration_msec = (datetime.now() - start).total_seconds() * 1000
        app.logger.info(
            "Search result for: {} returned: {} results and took {} msec".format(
                query, len(pictures), duration_msec
            )
        )

        results = {"results": [image.to_dict() for image in pictures]}
        return results, 200
