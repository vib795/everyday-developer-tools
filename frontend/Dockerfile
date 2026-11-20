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

# A release line, not the floating `alpine` tag. A floating tag carries no
# version, so Dependabot had nothing to track here and a base-image security
# release would only arrive on an unrelated rebuild. `1.31-alpine` is the same
# digest `alpine` resolves to today, so this changes nothing now -- it makes
# the next change visible. Patch releases still flow in on rebuild and
# Dependabot proposes the jump when a new line ships, matching how
# `python:3.14-slim` and `node:26-alpine` are pinned.
FROM nginx:1.31-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
