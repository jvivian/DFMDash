# syntax=docker/dockerfile:1

FROM --platform=linux/amd64 python:3.9-slim-buster

ENV POETRY_VERSION=1.4 \
    POETRY_VIRTUALENVS_CREATE=false


# Install dev tools
RUN apt-get update -y && apt-get install git -y

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
# COPY poetry.lock pyproject.toml /code/

# Copy Python code to the Docker image
COPY . /code/

# Project initialization:
RUN poetry install --no-interaction

ENTRYPOINT ["poetry", "run", "c19dfm"]
CMD ["--help"]
