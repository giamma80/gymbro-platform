/**
 * Jest Setup for Apollo Gateway Tests
 */

// Set test timeout
jest.setTimeout(10000);

// Setup global test environment
global.console = {
  ...console,
  // Suppress logs during tests unless VERBOSE is set
  log: process.env.VERBOSE ? console.log : jest.fn(),
  info: process.env.VERBOSE ? console.info : jest.fn(),
  warn: console.warn,
  error: console.error,
};

// Global test utilities
global.delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));