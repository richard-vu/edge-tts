# Stage 1: Build the React application using .env.pro
FROM node:24-alpine AS builder

RUN corepack enable

WORKDIR /app

# Install dependencies first for optimal Docker layer caching
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy project source files
COPY . .

# Mandatory .env.pro configuration (build fails if .env.pro is missing)
COPY .env.pro ./.env.pro
COPY .env.pro ./.env

# Type-check and build strictly with production (.env.pro) mode
RUN pnpm exec tsc -b && pnpm exec vite build --mode pro

# Stage 2: Serve static files with Nginx (with SPA routing support)
FROM nginx:stable-alpine AS runner

# Configure Nginx for React Router SPA fallback
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

