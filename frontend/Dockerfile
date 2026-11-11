# Matches the `spa` stage of the root Dockerfile, which is what Render actually
# builds production from -- so this image and production compile the SPA on the
# same Node rather than drifting apart. 20 also tripped an npm EBADENGINE
# warning, since react-router declares node >=22.22.0, and the 20 line stopped
# getting security updates in April 2026.
FROM node:26-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
# No --legacy-peer-deps: the peer-dep tree resolves cleanly on its own now
# (vite@8 and @vitejs/plugin-react@6 are compatible). Keeping the flag would
# silently re-admit genuinely broken peer ranges on the next dependency bump.
RUN npm ci --no-audit --no-fund
COPY . ./
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
