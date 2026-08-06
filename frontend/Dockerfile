# --- Stage 1: Build dependencies & Next.js static assets ---
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependency configs
COPY package.json ./

# Install packages (using npm install because package-lock.json might not be checked in)
RUN npm install

# Copy application sources
COPY . .

# Run next.js compile
RUN npm run build

# --- Stage 2: Production runtime runner ---


FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Copy output assets and dependencies
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./

EXPOSE 3000

CMD ["npm", "run", "start"]
