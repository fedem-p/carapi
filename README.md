# carapi

## Getting started

build container:

```sh
docker build -t autoscout_scraper .
```

run linting:

```sh
docker run --rm -v $(pwd):/app autoscout_scraper bash ./lint.sh
```

run tests:

```sh
docker run --rm -v $(pwd):/app autoscout_scraper bash ./test.sh
```

run app:

```sh
docker compose build && docker compose up
```


update make and models:

```sh
docker run --rm -v $(pwd):/app autoscout_scraper bash ./update_make_models.sh
```