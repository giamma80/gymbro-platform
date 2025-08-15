/**
 * 🚀 MINIMAL GraphQL Gateway Server 
 * Following EXACT Render.com deployment playbook from User Management Service v0.1.3
 * 
 * ✅ LESSON LEARNED: Start minimal, add complexity gradually
 * ✅ Deploy Strategy: Basic app + health check FIRST
 */

import express from 'express';
import cors from 'cors';
import { config } from './config';

async function startMinimalServer(): Promise<void> {
  try {
    // ✅ LESSON LEARNED: Dynamic PORT binding critical for Render.com
    const PORT = parseInt(process.env['PORT'] || '4000', 10);
    
    console.log('🚀 Starting MINIMAL GymBro GraphQL Gateway v0.2.0');
    console.log(`📍 Environment: ${config.NODE_ENV}`);
    console.log(`🚪 Port: ${PORT}`);

    // Create Express app
    const app = express();

    // ✅ LESSON LEARNED: CORS permissive for MVP/debug
    app.use(cors({
      origin: true,
      credentials: true
    }));

    app.use(express.json());

    // ✅ LESSON LEARNED: Essential health check endpoints
    // /ping - minimal connectivity test
    app.get('/ping', (req, res) => {
      res.status(200).json({ 
        ping: 'pong',
        timestamp: new Date().toISOString(),
        service: 'graphql-gateway-minimal',
        version: '0.2.0'
      });
    });

    // /health - basic health check
    app.get('/health', (req, res) => {
      res.status(200).json({
        status: 'healthy',
        service: 'graphql-gateway-minimal',
        version: '0.2.0',
        timestamp: new Date().toISOString(),
        environment: config.NODE_ENV,
        port: PORT
      });
    });

    // Placeholder GraphQL endpoint (without Apollo for now)
    app.post('/graphql', (req, res) => {
      res.status(200).json({
        data: {
          __typename: 'Query',
          placeholder: 'GraphQL Gateway is healthy - Apollo integration coming next!'
        }
      });
    });

    app.get('/graphql', (req, res) => {
      res.status(200).json({
        message: 'GraphQL Gateway Minimal Server',
        version: '0.2.0',
        endpoints: ['/ping', '/health', '/graphql']
      });
    });

    // Start server
    const server = app.listen(PORT, '0.0.0.0', () => {
      console.log(`✅ Minimal GraphQL Gateway running on http://0.0.0.0:${PORT}`);
      console.log(`🏥 Health check: http://0.0.0.0:${PORT}/health`);
      console.log(`📍 Ping endpoint: http://0.0.0.0:${PORT}/ping`);
      console.log(`🚀 GraphQL endpoint: http://0.0.0.0:${PORT}/graphql`);
    });

    // Graceful shutdown
    process.on('SIGTERM', () => {
      console.log('🛑 SIGTERM received, shutting down gracefully');
      server.close(() => {
        console.log('✅ Server closed');
        process.exit(0);
      });
    });

    process.on('SIGINT', () => {
      console.log('🛑 SIGINT received, shutting down gracefully');
      server.close(() => {
        console.log('✅ Server closed');
        process.exit(0);
      });
    });

  } catch (error) {
    console.error('❌ Failed to start minimal server:', error);
    process.exit(1);
  }
}

// Start the server
startMinimalServer();
