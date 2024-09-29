FROM python:3.12.3

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN --mount=type=cache,mode=0755,target=/root/.cache \
  pip install -r requirements.txt

COPY ./src ./src

CMD ["fastapi", "run", "src/main.py", "--port", "3000"]
