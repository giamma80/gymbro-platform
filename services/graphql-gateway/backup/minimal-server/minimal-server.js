/**
 * 🚨 MINIMAL SERVER for GraphQL Gateway Debugging
 * Following User Management Service deployment lessons:
 * ✅ Dynamic PORT binding
 * ✅ Basic health checks
 * ✅ Minimal dependencies
 */

const express = require('express');

async function startMinimalServer() {
    try {
        // ✅ ROBUST PORT PARSING for Render.com
        let PORT = parseInt(process.env.PORT, 10);

        // Fallback if PORT is NaN, undefined, or invalid
        if (!PORT || isNaN(PORT) || PORT <= 0 || PORT >= 65536) {
            PORT = 4000;
            console.log('⚠️  PORT env var invalid or missing, using fallback:', PORT);
        }

        console.log('🚀 Starting MINIMAL GraphQL Gateway v0.2.0');
        console.log(`📍 Environment: ${process.env.NODE_ENV || 'development'}`);
        console.log(`🚪 Port: ${PORT} (type: ${typeof PORT})`);
        console.log(`🔧 Original PORT env: "${process.env.PORT}" (type: ${typeof process.env.PORT})`);

        const app = express();

        // ✅ LESSON LEARNED: Essential health check endpoints
        app.get('/ping', (req, res) => {
            console.log('📍 Ping endpoint hit');
            res.status(200).json({
                ping: 'pong',
                timestamp: new Date().toISOString(),
                service: 'graphql-gateway-minimal',
                version: '0.2.0'
            });
        });

        app.get('/health', (req, res) => {
            console.log('🏥 Health endpoint hit');
            res.status(200).json({
                status: 'healthy',
                service: 'graphql-gateway-minimal',
                version: '0.2.0',
                timestamp: new Date().toISOString()
            });
        });

        // Default route
        app.get('/', (req, res) => {
            res.status(200).json({
                message: 'GymBro GraphQL Gateway - Minimal Debug Server',
                version: '0.2.0',
                endpoints: ['/ping', '/health']
            });
        });

        app.listen(PORT, '0.0.0.0', () => {
            console.log(`✅ Minimal server running on http://0.0.0.0:${PORT}`);
            console.log(`🔍 Test with: curl http://localhost:${PORT}/ping`);
        });

    } catch (error) {
        console.error('❌ Server startup failed:', error);
        process.exit(1);
    }
}

startMinimalServer();
