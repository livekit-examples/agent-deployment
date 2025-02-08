FROM node:20-slim AS base

WORKDIR /app

RUN npm install -g pnpm@9.7.0

FROM base AS build

RUN apt-get update -qq && apt-get install --no-install-recommends -y ca-certificates
COPY --link . .

RUN pnpm install --frozen-lockfile
RUN npm run build

FROM base
COPY --from=build /app /app
COPY --from=build /etc/ssl/certs /etc/ssl/certs

EXPOSE 8081
CMD [ "node", "./dist/agent.js", "start" ]
