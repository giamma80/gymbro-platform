import { ApolloGateway, IntrospectAndCompose } from '@apollo/gateway';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import { ApolloServerPluginLandingPageLocalDefault } from '@apollo/server/plugin/landingPage/default';
import express from 'express';
import http from 'http';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { logger } from './utils/logger.js';
import { getConfig } from './config/index.js';

// Load environment variables
dotenv.config();

async function startGateway() {
  try {
    const config = getConfig();
    
    // Create Apollo Gateway
    const gateway = new ApolloGateway({
      supergraphSdl: new IntrospectAndCompose({
        subgraphs: config.subgraphs,
        pollIntervalInMs: config.gateway.pollInterval,
      }),
      // Remove the buildService override - let it use defaults
    });

    // Create Apollo Server with Gateway
    const server = new ApolloServer({
      gateway,
      introspection: config.graphql.introspection,
      // Enable Apollo Studio local default landing page for development
      plugins: [
        // Use the local default landing page with embedded Explorer
        ApolloServerPluginLandingPageLocalDefault({ embed: true }),
        {
          requestDidStart() {
            return {
              didResolveOperation(requestContext) {
                logger.info(`GraphQL Operation: ${requestContext.request.operationName}`);
              },
            };
          },
        },
      ],
      formatError: (err) => {
        logger.error('GraphQL Error:', err);
        return {
          message: err.message,
          code: err.extensions?.code,
          path: err.path,
        };
      },
    });

    // Start the server
    await server.start();
    logger.info('Apollo Server started successfully');

    // Create Express app
    const app = express();
    const httpServer = http.createServer(app);

    // Middleware
    app.use(helmet({
      contentSecurityPolicy: false,
      crossOriginEmbedderPolicy: false,
    }));

    app.use(cors({
      origin: config.cors.origins,
      credentials: true,
    }));

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.status(200).json({
        status: 'ok',
        service: 'apollo-gateway',
        timestamp: new Date().toISOString(),
        environment: config.environment,
      });
    });

    // GraphQL endpoint
    app.use(
      config.graphql.path,
      express.json(),
      expressMiddleware(server, {
        context: async ({ req }) => {
          return {
            headers: req.headers,
            user: req.user, // Will be set by auth middleware if needed
          };
        },
      }),
    );

    // Start HTTP server
    httpServer.listen(config.server.port, config.server.host, () => {
      logger.info(`🚀 Apollo Gateway ready at http://${config.server.host}:${config.server.port}${config.graphql.path}`);
      logger.info(`🏥 Health check available at http://${config.server.host}:${config.server.port}/health`);
      logger.info(`📊 Apollo Studio available at https://studio.apollographql.com/`);
    });

    // Graceful shutdown
    process.on('SIGTERM', async () => {
      logger.info('SIGTERM received, shutting down gracefully');
      await server.stop();
      httpServer.close(() => {
        logger.info('Process terminated');
        process.exit(0);
      });
    });

  } catch (error) {
    logger.error('Failed to start Apollo Gateway:', error);
    process.exit(1);
  }
}

// Start the gateway
startGateway().catch((error) => {
  logger.error('Unhandled error during gateway startup:', error);
  process.exit(1);
});