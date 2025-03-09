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