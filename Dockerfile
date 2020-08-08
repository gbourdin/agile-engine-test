FROM python:3.8-buster

RUN mkdir -p /app
COPY ./image_search_api /app/image_search_api
COPY ./setup.py /app/setup.py

WORKDIR /app
RUN python setup.py install

EXPOSE 8080

CMD ["image_search_api run-uwsgi"]