ARG NODE_IMAGE=docker.io/library/node:20-bookworm-slim
ARG ALPINE_IMAGE=docker.io/library/alpine:3.21

FROM ${NODE_IMAGE} AS builder

WORKDIR /app
RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM ${ALPINE_IMAGE} AS dist

WORKDIR /opt/frontend
COPY --from=builder /app/dist ./dist

CMD ["sh", "-c", "mkdir -p /dist && cp -r /opt/frontend/dist/. /dist/"]
