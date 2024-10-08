# 
FROM python:3.12 as req-stage

WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt


FROM python:3.12

WORKDIR /api
COPY --from=req-stage /tmp/requirements.txt /api/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt
COPY ./api ./api

ENV IN_DOCKER_CONTAINER=true

#
CMD ["fastapi", "run", "api/main.py", "--port", "80"]