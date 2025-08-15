/**
 * 🏋️ GymBro Platform - Logger Utility
 * Simple structured logging for GraphQL Gateway
 */

import { config } from '../config';

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

class Logger {
    private logLevel: LogLevel;

    constructor() {
        this.logLevel = config.LOG_LEVEL as LogLevel;
    }

    private shouldLog(level: LogLevel): boolean {
        const levels: Record<LogLevel, number> = {
            debug: 0,
            info: 1,
            warn: 2,
            error: 3
        };

        return levels[level] >= levels[this.logLevel];
    }

    private formatMessage(level: LogLevel, message: string, meta?: any): string {
        const timestamp = new Date().toISOString();
        const baseLog = {
            timestamp,
            level: level.toUpperCase(),
            service: 'graphql-gateway',
            message,
            ...(meta && { meta })
        };

        return JSON.stringify(baseLog);
    }

    debug(message: string, meta?: any): void {
        if (this.shouldLog('debug')) {
            console.log(this.formatMessage('debug', message, meta));
        }
    }

    info(message: string, meta?: any): void {
        if (this.shouldLog('info')) {
            console.log(this.formatMessage('info', message, meta));
        }
    }

    warn(message: string, meta?: any): void {
        if (this.shouldLog('warn')) {
            console.warn(this.formatMessage('warn', message, meta));
        }
    }

    error(message: string, error?: Error | any): void {
        if (this.shouldLog('error')) {
            const meta = error instanceof Error
                ? { error: error.message, stack: error.stack }
                : { error };
            console.error(this.formatMessage('error', message, meta));
        }
    }
}

export const logger = new Logger();
