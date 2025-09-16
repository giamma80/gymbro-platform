import { logger } from '../utils/logger.js';

const requiredEnvVars = [
  'NODE_ENV',
  'GATEWAY_PORT',
];

export function getConfig() {
  const config = {
    environment: process.env.NODE_ENV || 'development',
    
    server: {
      port: parseInt(process.env.GATEWAY_PORT) || 4000,
      host: process.env.GATEWAY_HOST || '0.0.0.0',
    },

    graphql: {
      path: process.env.GRAPHQL_PATH || '/graphql',
      introspection: process.env.ENABLE_INTROSPECTION === 'true' || process.env.NODE_ENV !== 'production',
      playground: process.env.ENABLE_PLAYGROUND === 'true' || process.env.NODE_ENV !== 'production',
    },

    gateway: {
      pollInterval: parseInt(process.env.POLL_INTERVAL) || 30000, // 30 seconds
    },

    cors: {
      origins: process.env.CORS_ORIGINS 
        ? process.env.CORS_ORIGINS.split(',')
        : ['http://localhost:3000', 'http://localhost:8080'],
    },

    // Subgraphs configuration - Environment-based URLs
    subgraphs: [
      {
        name: 'user-management',
        url: process.env.NODE_ENV === 'production' 
          ? process.env.USER_MANAGEMENT_URL || 'https://gymbro-user-management.onrender.com/graphql'
          : process.env.USER_MANAGEMENT_URL || 'http://localhost:8001/graphql',
      },
      {
        name: 'calorie-balance', 
        url: process.env.NODE_ENV === 'production'
          ? process.env.CALORIE_BALANCE_URL || 'https://gymbro-calorie-balance.onrender.com/graphql'
          : process.env.CALORIE_BALANCE_URL || 'http://localhost:8002/graphql',
      },
      // Future subgraphs (commented out until GraphQL is implemented)
      // {
      //   name: 'meal-tracking',
      //   url: process.env.NODE_ENV === 'production'
      //     ? process.env.MEAL_TRACKING_URL || 'https://gymbro-meal-tracking.onrender.com/graphql'
      //     : process.env.MEAL_TRACKING_URL || 'http://localhost:8003/graphql',
      // },
      // {
      //   name: 'health-monitor',
      //   url: process.env.NODE_ENV === 'production'
      //     ? process.env.HEALTH_MONITOR_URL || 'https://gymbro-health-monitor.onrender.com/graphql'
      //     : process.env.HEALTH_MONITOR_URL || 'http://localhost:8004/graphql',
      // },
      // {
      //   name: 'ai-coach',
      //   url: process.env.NODE_ENV === 'production'
      //     ? process.env.AI_COACH_URL || 'https://gymbro-ai-coach.onrender.com/graphql'
      //     : process.env.AI_COACH_URL || 'http://localhost:8005/graphql',
      // },
      // {
      //   name: 'notifications',
      //   url: process.env.NODE_ENV === 'production'
      //     ? process.env.NOTIFICATIONS_URL || 'https://gymbro-notifications.onrender.com/graphql'
      //     : process.env.NOTIFICATIONS_URL || 'http://localhost:8006/graphql',
      // },
    ],

    logging: {
      level: process.env.LOG_LEVEL || 'info',
      format: process.env.NODE_ENV === 'production' ? 'json' : 'combined',
    },
  };

  // Validate required environment variables in production
  if (config.environment === 'production') {
    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
    if (missingVars.length > 0) {
      const message = `Missing required environment variables: ${missingVars.join(', ')}`;
      logger.error(message);
      throw new Error(message);
    }
  }

  // Filter out unreachable subgraphs in development
  if (config.environment === 'development') {
    logger.info('Development mode: Filtering available subgraphs...');
    // In development, we can dynamically check which services are available
    // For now, we'll include all configured subgraphs
  }

  logger.info('Configuration loaded successfully', {
    environment: config.environment,
    port: config.server.port,
    subgraphs: config.subgraphs.map(sg => ({ name: sg.name, url: sg.url })),
  });

  return config;
}