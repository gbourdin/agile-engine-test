import logging
from flask import Flask, redirect, url_for
from typing import Any

from .api import search_blueprint
from .models.pictures import PicturesCache


def configure_app(app) -> None:
    app.config.from_object("image_search_api.settings.default")
    app.url_map.strict_slashes = False

    app.logger.setLevel(logging.INFO)
    app.pictures_cache = PicturesCache()
    app.logger.info("Start: Refreshing Cache")
    app.pictures_cache.update_cache()
    app.logger.info("Finished: Refreshing Cache")


def initialize_app(app) -> None:
    configure_app(app)
    # Namespaces should be added here, not in api init.
    app.register_blueprint(search_blueprint)


def create_app() -> Any:
    app = Flask(__name__, instance_relative_config=True)

    @app.route("/")
    def search():
        return redirect(url_for("search.doc"))

    initialize_app(app)

    return app
