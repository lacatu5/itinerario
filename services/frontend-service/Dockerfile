FROM node:20-alpine as builder

WORKDIR /app

COPY services/frontend-service/package*.json ./

RUN npm install

COPY services/frontend-service/ ./

ARG VITE_API_URL=https://api.itinerario.app
ARG VITE_CENTRIFUGO_WS_URL=wss://api.itinerario.app/connection/websocket

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_CENTRIFUGO_WS_URL=${VITE_CENTRIFUGO_WS_URL}

RUN npm run build:prod

FROM nginx:alpine AS stage-1

COPY --from=builder /app/dist /usr/share/nginx/html

COPY services/frontend-service/nginx.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
