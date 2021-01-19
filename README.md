# Open Coverage

Open source project for providing coverage reporting

## Develop

```
make install-dev
```

## Run tests

Run docker compose first:

```
docker-compose up
```

```
make test
```

## Run

```
make run
```

## Send report from CI

```
codecov --url="http://localhost:8000" --token=foobar --slug=vangheem/guillotina
```
