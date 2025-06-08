# Build stage
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
# Генерируем package-lock.json из package.json
RUN npm install --package-lock-only
# Теперь CI установит ровно то, что в lock-файле
RUN npm ci
RUN npm install -g webpack-cli webpack-dev-server

COPY . .

RUN mkdir -p public && mv index.html public/

RUN npm run build

# Production stage
FROM node:18-slim

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public

ENV NODE_ENV=production \
    NPM_CONFIG_LEGACY_PEER_DEPS=true

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["npm", "start"]
