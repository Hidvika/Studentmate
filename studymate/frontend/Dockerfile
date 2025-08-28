FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install --no-audit --no-fund

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--port", "3000", "--hostname", "0.0.0.0"]



