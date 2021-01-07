# Use non-root user to run the container
# Scan image for vulnerabilities using during or after CI build

FROM python:3.7.7-alpine3.11

RUN apk add --update && mkdir -p /usr/src

WORKDIR /usr/backend/src

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

RUN adduser -D backend_user && chown -R backend_user /usr

USER backend_user

# CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0"]
