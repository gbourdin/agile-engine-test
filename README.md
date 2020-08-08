# image_search_

Simple Flask + Flask-RESTPlus api to serve machine learning predictors


I will only implement full string matching. Fuzzy search, partial and full text
I would never implement manually. And would most likely be using the db engine
for that.

Index update could be a lot smarter. Chose a naive implementation.

TODO:
* Async fetch. Picture download and cache update should be done by a celery task
* Validation
* Search