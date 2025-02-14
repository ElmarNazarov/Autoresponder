FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
