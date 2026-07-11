FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
# No -s: dist/serve.json rewrites only client routes to index.html, so the
# prerendered /, /login, /register pages are served as real static HTML.
CMD ["sh", "-c", "serve dist --listen tcp://0.0.0.0:$PORT"]
