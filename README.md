# image_search_api

Simple flask api to expose a search microservice for an Agile Engine challenge

## How to Use
There's two alternatives to running this project. As a whole system, 
using docker compose, or just running the backed locally using python. 

### Using docker compose
A `docker-compose.yml`  file is provided to make it easier to get the system 
up and running.

The only requirement for this is having docker-ce up and running in your host.

Once you've installed docker in your computer, simply run 
`docker-compose up` which will build the images and start the server.

Once the cache has updated, you can now test it by going to 
http://localhost:8000/api/v1.0/search in your browser or typing 
`curl -X GET "http://localhost:8080/api/v1.0/search/nikon" -H "accept: application/json"`
in a terminal.

### Locally with python
To run locally you'll need to have a python 3.8 (3.7 should work too) installation.

Once you've set up python, create a venv to test this project and activate it:

```bash
python3 -m venv ~/.venvs/search-api
source ~/.venvs/search-api/bin/activate
```

And now install the project requirements and run it!
```bash
python setup.py install
image_search_api run-uwsgi
```

As with the docker version, you can now test it by going to 
http://localhost:8000/api/v1.0/search in your browser or typing 
`curl -X GET "http://localhost:8080/api/v1.0/search/nikon" -H "accept: application/json"`
in a terminal. 

I will only implement full string matching. Fuzzy search, partial and full text
I would never implement manually. And would most likely be using the db engine
for that.

#### For development purposes
If you're going to be making changes to the code and want to test them using
 live-reload, make an editable installation instead and use the development server
```bash
pip install -e .
image_search_api run-server
```

## A few notes on implementation:

### Regarding the search algorithm
I chose to go with a  simple search algorithm that relies on a very naive in memory index.
Each feature from a picture (author, camera and tags) is tokenized and its tokens indexed.
Running a search does the following:
* Tokenize the search term: "Nikon D800" becomes: ["nikon d800", "nikon", "d800"]
* Search the tokens in all the indexes and simply pile up any images that match
* Sort results by popularity: Images that matched more times will be brought 
to the front, so pictures where camera was "Nikon d800", will be shown 
before those where the camera was "Nikon D90"


### Regarding the tech stack

I chose to use flask + flask rest plus as I had a cookiecutter for that stack handy.
However, flask-restplus has been abandoned and development 
continues as [flask-restx](https://github.com/python-restx/flask-restx) I might
port the code to that just for fun. I would not have gone with this for production use today.



### What's missing
1. I would have gone with a different cache backend. With a few ideas in mind:
    - Allow concurrent non-blocking access to the database
    - Enable multi-process, multi-thread (I disabled it on purpose for this test)
    - Allow cache updates and index updates to run in a non-blocking fashion

    I would have stored the picture metadata in a SQL database, and kept the index data in a simpler key-value store.
    When a search runs, I would retrieve the indexes, run the search algorithm and then fetch the matching items from the database.

2. Index update currently runs with a cron-job that hits an endpoint meant for this. I would have kept this logic, but probably securing the endpoint.

3. I would have added a message broker rabbitmq and used celery to run async tasks then do the following:
    - On index updates: Enqueue a task per image
    - Set up celery-beat to manage periodic index updates

4. Better search: Honestly I wouldnt try to implement a search algorithm 
manually. Postgresql has a great full text search feature and if that's not enought
there's always fully mature search backends like elasticsearch that can be used
to work on things like this.

5. TESTS! This really needs unit tests!


## Design
T.B.D.