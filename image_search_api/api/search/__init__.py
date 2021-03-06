from flask import Blueprint
from flask_restx import Api

from .endpoints import search_ns, cache_ns

blueprint = Blueprint("search", __name__, url_prefix="/api/v1.0")
api = Api(
    blueprint,
    version="1.0",
    title="Image search",
    description="Image Search  API",
    doc="/doc/",
)

api.namespaces.clear()
api.add_namespace(search_ns)
api.add_namespace(cache_ns)
