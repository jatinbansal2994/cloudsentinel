# Stage 1 — build the Vite app
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# VITE_ vars must be baked in at build time (Vite embeds them in the JS bundle)
ARG VITE_API_ENDPOINT
ARG VITE_USER_POOL_ID
ARG VITE_USER_POOL_CLIENT_ID

ENV VITE_API_ENDPOINT=$VITE_API_ENDPOINT
ENV VITE_USER_POOL_ID=$VITE_USER_POOL_ID
ENV VITE_USER_POOL_CLIENT_ID=$VITE_USER_POOL_CLIENT_ID

RUN npm run build

# Stage 2 — serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
