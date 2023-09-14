# On production will use tiangolo/uvicorn-gunicorn-fastapi:python3.11 (just for fun)
FROM python:3.12.0rc2

WORKDIR /code

# Install requirements
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install -U pytest pytest-cov
#RUN pip install pytest-docker-compose
RUN pip install --no-cache-dir --upgrade requests

# Using uvicorn service for async fastapi. No nginx proxy
COPY ./app /code/app
COPY ./tests /code/tests
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
CMD sleep 10 && pytest -vv --cov=app ./tests/test_*
