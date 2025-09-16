import winston from 'winston';

const { combine, timestamp, errors, json, colorize, simple, printf } = winston.format;

// Custom format for development
const devFormat = printf(({ level, message, timestamp, ...meta }) => {
  let log = `${timestamp} [${level}] ${message}`;
  
  if (Object.keys(meta).length > 0) {
    log += `\n${JSON.stringify(meta, null, 2)}`;
  }
  
  return log;
});

// Create logger
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: combine(
    timestamp(),
    errors({ stack: true })
  ),
  defaultMeta: { service: 'apollo-gateway' },
  transports: [
    // Console transport
    new winston.transports.Console({
      format: process.env.NODE_ENV === 'production' 
        ? combine(json())
        : combine(colorize(), devFormat)
    }),
  ],
});

// Add file transport in production
if (process.env.NODE_ENV === 'production') {
  logger.add(new winston.transports.File({
    filename: 'logs/gateway-error.log',
    level: 'error',
    format: combine(timestamp(), json())
  }));
  
  logger.add(new winston.transports.File({
    filename: 'logs/gateway-combined.log',
    format: combine(timestamp(), json())
  }));
}

export default logger;