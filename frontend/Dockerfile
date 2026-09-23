# Frontend dev image (Vite dev server).
FROM node:22-alpine

WORKDIR /app

# Install deps into the image layer. At runtime a named volume holds /app/node_modules so the
# host bind mount (source code) doesn't overlay them — nothing installs on Windows.
COPY package.json ./
RUN npm install

EXPOSE 5173
CMD ["npm", "run", "dev"]
