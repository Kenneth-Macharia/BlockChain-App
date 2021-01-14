FROM node:14-alpine3.11

RUN apk add --update && mkdir -p /usr/src

WORKDIR /usr/src/frontend

COPY package-lock.json package.json ./

RUN npm i --no-cache

EXPOSE 3000

COPY . .

RUN adduser -D azureuser && chown -R azureuser /usr

USER azureuser

CMD ["npm", "start"]
