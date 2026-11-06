FROM node:22-alpine AS build
WORKDIR /app
COPY frontend_react/package*.json ./
RUN npm ci
COPY frontend_react .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
