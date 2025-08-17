/**
 * 🏋️ GymBro Platform - GraphQL Gateway v0.2.1
 * Main server entry point with Render.com deployment optimizations
 * 
 * Applies all lessons learned from User Management v0.1.3 deployment:
 * ✅ Dynamic PORT binding
 * ✅ Health check endpoints (/health + /ping)
 * ✅ CORS permissive for MVP debugging
 * ✅ Minimal middleware initially
 * ✅ Proper error handling
 * ✅ Apollo Federation with schema refresh
 */

import { ApolloGateway, IntrospectAndCompose } from '@apollo/gateway';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import compression from 'compression';
import cors from 'cors';
import express from 'express';
import helmet from 'helmet';
import { createServer } from 'http';
import morgan from 'morgan';
import { config } from './config';
import { logger } from './utils/logger';

interface Context {
    req: express.Request;
    res: express.Response;
}

async function startServer(): Promise<void> {
    try {
        logger.info('🚀 Starting GymBro GraphQL Gateway v0.2.0');
        logger.info(`📍 Environment: ${config.NODE_ENV}`);
        logger.info(`🚪 Port: ${config.PORT}`);

        // Create Express app
        const app = express();

        // ✅ LESSON LEARNED: Minimal security middleware initially
        // TrustedHostMiddleware can cause hanging - add gradually
        app.use(helmet({
            contentSecurityPolicy: config.NODE_ENV === 'production',
            crossOriginEmbedderPolicy: false
        }));

        // ✅ LESSON LEARNED: CORS permissive for MVP/debug
        // Render health checks come from internal domains
        app.use(cors({
            origin: config.CORS_ORIGINS === '*' ? true : config.CORS_ORIGINS.split(','),
            credentials: true
        }));

        app.use(compression());
        app.use(morgan(config.NODE_ENV === 'production' ? 'combined' : 'dev'));

        // ✅ CRITICAL: JSON body parsing middleware for Apollo Server
        app.use(express.json());
        app.use(express.urlencoded({ extended: true }));

        // ✅ LESSON LEARNED: Essential health check endpoints
        // /ping - minimal connectivity test
        app.get('/ping', (req, res) => {
            res.status(200).json({
                ping: 'pong',
                timestamp: new Date().toISOString(),
                service: 'graphql-gateway',
                version: '0.2.0'
            });
        });

        // /health - basic health check
        app.get('/health', (req, res) => {
            res.status(200).json({
                status: 'healthy',
                service: 'graphql-gateway',
                version: '0.2.0',
                timestamp: new Date().toISOString()
            });
        });

        // /health/detailed - comprehensive health check
        app.get('/health/detailed', async (req, res) => {
            try {
                const healthStatus = {
                    status: 'healthy',
                    service: 'graphql-gateway',
                    version: '0.2.0',
                    timestamp: new Date().toISOString(),
                    environment: config.NODE_ENV,
                    port: config.PORT,
                    uptime: process.uptime(),
                    memory: process.memoryUsage(),
                    subgraphs: {} as Record<string, any>
                };

                // Test subgraph connectivity
                try {
                    const response = await fetch(`${config.USER_MANAGEMENT_URL.replace('/graphql', '')}/health`);
                    healthStatus.subgraphs['user-management'] = {
                        url: config.USER_MANAGEMENT_URL.replace('/graphql', ''),
                        status: response.ok ? 'healthy' : 'unhealthy',
                        responseTime: Date.now()
                    };
                } catch (error) {
                    healthStatus.subgraphs['user-management'] = {
                        url: config.USER_MANAGEMENT_URL.replace('/graphql', ''),
                        status: 'unhealthy',
                        error: error instanceof Error ? error.message : 'Unknown error'
                    };
                }

                res.status(200).json(healthStatus);
            } catch (error) {
                logger.error('Health check failed:', error);
                res.status(500).json({
                    status: 'unhealthy',
                    service: 'graphql-gateway',
                    error: error instanceof Error ? error.message : 'Unknown error',
                    timestamp: new Date().toISOString()
                });
            }
        });

        // Apollo Gateway setup
        const gateway = new ApolloGateway({
            supergraphSdl: new IntrospectAndCompose({
                subgraphs: [
                    {
                        name: 'user-management',
                        url: config.USER_MANAGEMENT_URL
                    }
                    // Future subgraphs will be added here following the same pattern
                ]
            }),
            debug: config.NODE_ENV !== 'production'
        });

        // Apollo Server setup
        const server = new ApolloServer<Context>({
            gateway,
            plugins: [
                // Add performance and security plugins as needed
            ],
            introspection: true, // Always enable introspection for Apollo Sandbox
            includeStacktraceInErrorResponses: config.NODE_ENV !== 'production'
        });

        // Start Apollo Server
        await server.start();
        logger.info('✅ Apollo Server started');

        // Apply GraphQL middleware
        app.use('/graphql', expressMiddleware(server, {
            context: async ({ req, res }): Promise<Context> => ({
                req,
                res
            })
        }));

        // Apollo Sandbox always enabled (prod & dev)
        app.get('/', (req, res) => {
            // Redirect to Apollo Sandbox with prefilled endpoint
            const endpoint = `https://${req.headers.host}/graphql`;
            res.redirect(`https://studio.apollographql.com/sandbox/explorer?endpoint=${encodeURIComponent(endpoint)}`);
        });

        // 404 handler
        app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Not Found',
                message: `Route ${req.originalUrl} not found`,
                service: 'graphql-gateway'
            });
        });

        // Global error handler
        app.use((error: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
            logger.error('Unhandled error:', error);
            res.status(500).json({
                error: 'Internal Server Error',
                message: config.NODE_ENV === 'production' ? 'Something went wrong' : error.message,
                service: 'graphql-gateway'
            });
        });

        // Create HTTP server
        const httpServer = createServer(app);

        // ✅ LESSON LEARNED: Listen on all interfaces for containers
        httpServer.listen(config.PORT, '0.0.0.0', () => {
            logger.info(`🚀 GraphQL Gateway running on http://0.0.0.0:${config.PORT}`);
            logger.info(`📊 GraphQL endpoint: http://0.0.0.0:${config.PORT}/graphql`);
            logger.info(`🏥 Health check: http://0.0.0.0:${config.PORT}/health`);
            logger.info(`🏓 Ping endpoint: http://0.0.0.0:${config.PORT}/ping`);
        });

        // Graceful shutdown
        process.on('SIGINT', async () => {
            logger.info('🛑 Received SIGINT, shutting down gracefully');
            await server.stop();
            httpServer.close(() => {
                logger.info('✅ Server stopped');
                process.exit(0);
            });
        });

        process.on('SIGTERM', async () => {
            logger.info('🛑 Received SIGTERM, shutting down gracefully');
            await server.stop();
            httpServer.close(() => {
                logger.info('✅ Server stopped');
                process.exit(0);
            });
        });

    } catch (error) {
        logger.error('❌ Failed to start server:', error);
        process.exit(1);
    }
}

// Start the server
startServer().catch((error) => {
    logger.error('❌ Startup error:', error);
    process.exit(1);
});

export { startServer };
