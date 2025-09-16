# Multi-stage build for production optimization
FROM node:18-alpine AS base

# Security: Install security updates
RUN apk update && apk upgrade && apk add --no-cache dumb-init

# Development stage
FROM base AS development
WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S apollo -u 1001 -G nodejs

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Set ownership
RUN chown -R apollo:nodejs /app
USER apollo

# Expose port
EXPOSE 4000

# Development command
CMD ["dumb-init", "npm", "run", "dev"]

# Production stage
FROM base AS production
WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S apollo -u 1001 -G nodejs

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code (only what's needed)
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create logs directory
RUN mkdir -p logs && chown -R apollo:nodejs logs

# Set ownership
RUN chown -R apollo:nodejs /app

# Switch to non-root user
USER apollo

# Expose port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node scripts/health-check.js || exit 1

# Start the gateway
CMD ["dumb-init", "node", "src/index.js"]