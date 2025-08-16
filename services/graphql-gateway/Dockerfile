# 🏋️ GymBro Platform - GraphQL Gateway
# Multi-stage Dockerfile seguendo deployment playbook v0.1.3

# ================================
# Stage 1: Builder
# ================================
FROM node:20-alpine AS builder

# Metadata
LABEL maintainer="GymBro Platform Team"
LABEL version="0.2.0"
LABEL description="GraphQL Gateway for GymBro Platform"

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci --only=production --silent

# Copy source code
COPY . .

# Build TypeScript to JavaScript
RUN npm run build

# ================================
# Stage 2: Production Runtime
# ================================
FROM node:20-alpine AS production

# Install security updates
RUN apk upgrade --no-cache

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S graphql -u 1001

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production --silent && \
    npm cache clean --force

# Copy built application from builder stage
COPY --from=builder --chown=graphql:nodejs /app/dist ./dist

# Validate that the main file exists
RUN ls -la dist/index.js || (echo "❌ ERROR: dist/index.js not found!" && exit 1)

# ✅ VALIDATION: Ensure Apollo Server files exist
RUN ls -la dist/ && test -f dist/index.js || { echo "❌ Apollo Server build failed!"; exit 1; }

# Switch to non-root user
USER graphql

# Expose port (will be overridden by Render's PORT env var)
EXPOSE 4000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 4000) + '/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# ✅ CRITICAL: Full Apollo Server with Federation 
# Upgraded from minimal server to complete GraphQL Gateway v0.2.1
# Force clean rebuild: 2025-08-16 post-cleanup
# MUST NOT USE MINIMAL SERVER FILES
CMD ["node", "dist/index.js"]
