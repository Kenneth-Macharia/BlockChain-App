FROM python:3.7.7-alpine3.11

RUN apk add --update && mkdir -p /usr/src

WORKDIR /usr/backend

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0"]
