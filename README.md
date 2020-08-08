# image_search_api

Simple flask api to expose a search microservice for an agiel-engine challenge

A few notes on implementation:


Running:
To run the full system, you'll need docker-ce and docker-compose
In that case, just run `docker-compose up` and then `curl -X GET "http://localhost:8080/api/v1.0/search/nikon" -H "accept: application/json"

To run locally:
Simply create a virtualenv with python 3.8 and then:
```
python setup.py install
image_search_api run-uwsgi
curl -X GET "http://localhost:8080/api/v1.0/search/nikon" -H "accept: application/json"
```

