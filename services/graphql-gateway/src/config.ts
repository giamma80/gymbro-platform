/**
 * 🏋️ GymBro Platform - GraphQL Gateway Configuration
 * Following deployment best practices from User Management Service
 * Updated: 2025-08-17 - Force redeploy after _service field fix
 */

export const config = {
    // ✅ LESSON LEARNED: Environment detection
    NODE_ENV: process.env['NODE_ENV'] || 'development',

    // ✅ LESSON LEARNED: Dynamic PORT for Render.com with robust parsing
    PORT: (() => {
        const portEnv = process.env['PORT'];
        if (!portEnv || portEnv.trim() === '') {
            console.log('⚠️ PORT environment variable is empty, using default 4000');
            return 4000;
        }
        const port = parseInt(portEnv.trim(), 10);
        if (isNaN(port) || port <= 0 || port >= 65536) {
            console.log(`⚠️ Invalid PORT value: "${portEnv}", using default 4000`);
            return 4000;
        }
        console.log(`✅ Using PORT: ${port}`);
        return port;
    })(),

    // ✅ LESSON LEARNED: CORS permissive for MVP/debug
    CORS_ORIGINS: process.env['CORS_ORIGINS'] || '*',

    // Service URLs - centralized configuration
    USER_MANAGEMENT_URL: process.env['USER_MANAGEMENT_URL'] || 'http://localhost:8001',

    // Future service URLs (will be added as services are implemented)
    CALORIE_SERVICE_URL: process.env['CALORIE_SERVICE_URL'] || 'http://localhost:8002',
    MEAL_SERVICE_URL: process.env['MEAL_SERVICE_URL'] || 'http://localhost:8002',
    ANALYTICS_SERVICE_URL: process.env['ANALYTICS_SERVICE_URL'] || 'http://localhost:8003',

    // Apollo Gateway Configuration
    APOLLO_GRAPH_REF: process.env['APOLLO_GRAPH_REF'] || '',
    APOLLO_KEY: process.env['APOLLO_KEY'] || '',

    // Security Configuration
    JWT_SECRET: process.env['JWT_SECRET'] || 'gymbro-dev-secret-change-in-production',

    // Rate Limiting (for future implementation)
    RATE_LIMIT_WINDOW_MS: parseInt(process.env['RATE_LIMIT_WINDOW_MS'] || '900000', 10), // 15 minutes
    RATE_LIMIT_MAX_REQUESTS: parseInt(process.env['RATE_LIMIT_MAX_REQUESTS'] || '100', 10),

    // Logging Configuration
    LOG_LEVEL: process.env['LOG_LEVEL'] || (process.env['NODE_ENV'] === 'production' ? 'info' : 'debug'),

    // Health Check Configuration
    HEALTH_CHECK_TIMEOUT: parseInt(process.env['HEALTH_CHECK_TIMEOUT'] || '5000', 10),
} as const;
