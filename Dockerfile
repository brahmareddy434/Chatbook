FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY . .

COPY .env .

RUN pip install -r requirements.txt
RUN pip install psycopg2


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]


