# ========================
# BUILD STAGE
# ========================
FROM node:18-alpine AS builder

# Install AI/ML dependencies and system tools
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    curl \
    git \
    tzdata \
    icu-data-full

# Configure global ICU for i18n
ENV NODE_ICU_DATA="/usr/share/icu"

WORKDIR /app

# Install dependencies with security audit
COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts && \
    npm audit fix --force && \
    rm -rf /root/.npm

# ========================
# PRODUCTION IMAGE
# ========================
FROM node:18-alpine

# Regional configuration
ENV TZ=UTC \
    NODE_ENV=production \
    LANG=en_US.UTF-8

# Security hardening
RUN apk add --no-cache \
    su-exec \
    dumb-init \
    ca-certificates && \
    addgroup -S node && \
    adduser -S node -G node

WORKDIR /app

# Copy built artifacts
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=node:node . .

# AI/Compliance configuration
COPY --from=deepseek/ai-runtime:v7 /ai-models ./ai-models

# Configure container security
RUN chmod -R g=u . && \
    find . -type d -exec chmod 755 {} + && \
    find . -type f -exec chmod 644 {} + && \
    chmod +x docker-entrypoint.sh

USER node:node

# Health check and monitoring
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8888/api/health || exit 1

# Multi-language/region support
RUN ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime && \
    echo "$TZ" > /etc/timezone

# Performance optimization
ENV NODE_CLUSTER_SCHED_POLICY=rr \
    NODE_OPTIONS="--max-old-space-size=4096 --experimental-vm-modules"

# Entrypoint with graceful shutdown
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["su-exec", "node:node", "npm", "run", "start:cluster"]

# ========================
# RUNTIME ENHANCEMENTS
# ========================
EXPOSE 8888 5000 9090
STOPSIGNAL SIGTERM

# ========================
# COMPLIANCE & AI INTEGRATION
# ========================
LABEL org.opencontainers.image.title="RLG Projects" \
      org.opencontainers.image.description="Global Remote Work Orchestration Platform" \
      org.opencontainers.image.vendor="RLG Innovations" \
      com.rlg.compliance.gdpr="true" \
      com.rlg.ai.version="7b-chat-v2"

      # ADD THESE FOR PRODUCTION:
# RUN microdnf install openssl && \
#     update-ca-trust force-enable && \
#     npm config set strict-ssl true