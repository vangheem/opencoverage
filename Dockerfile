FROM python:3.8.7-buster
LABEL maintainer="."

WORKDIR /app

RUN apt-get update && apt-get install -y vim netcat curl

# Utilizing poetry's install script sandboxes poetry's dependencies away from the system
# Otherwise applications may trample a package poetry requires, breaking poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - --version=1.1.4

# This is a bit of a hack ATM as $HOME is not set when docker is built
# This will need to be updated if we install poetry as a non-root user
ENV PATH="/root/.poetry/bin:$PATH"

RUN poetry config virtualenvs.create false

COPY . /app

RUN make install

EXPOSE 5000

RUN mkdir /conf
CMD ["make", "run"]
