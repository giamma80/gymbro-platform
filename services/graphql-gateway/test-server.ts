/**
 * 🏋️ GymBro Platform - GraphQL Gateway Test Server
 * Simplified version for debugging
 */

import express from 'express';

async function startTestServer(): Promise<void> {
  const app = express();
  const PORT = 4000;

  // Simple ping endpoint
  app.get('/ping', (req, res) => {
    res.json({ 
      ping: 'pong',
      timestamp: new Date().toISOString(),
      service: 'graphql-gateway-test',
      version: '0.2.0'
    });
  });

  // Simple health endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      service: 'graphql-gateway-test',
      version: '0.2.0',
      timestamp: new Date().toISOString()
    });
  });

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Test GraphQL Gateway running on http://localhost:${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`🏓 Ping endpoint: http://localhost:${PORT}/ping`);
  });
}

startTestServer().catch(console.error);
