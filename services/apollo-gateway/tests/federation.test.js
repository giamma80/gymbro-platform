/**
 * Integration Tests for Apollo Federation Gateway
 * Tests federation across user-management and calorie-balance services
 */

import http from 'http';
import { jest } from '@jest/globals';

const GATEWAY_URL = process.env.GATEWAY_URL || 'http://localhost:4000';
const GRAPHQL_ENDPOINT = `${GATEWAY_URL}/graphql`;
const HEALTH_ENDPOINT = `${GATEWAY_URL}/health`;

// Helper function to make GraphQL requests
async function graphqlRequest(query, variables = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ query, variables });
    
    const options = {
      hostname: 'localhost',
      port: 4000,
      path: '/graphql',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    };

    const req = http.request(options, (res) => {
      let body = '';
      
      res.on('data', (chunk) => {
        body += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          resolve({
            status: res.statusCode,
            data: result,
          });
        } catch (error) {
          reject(new Error(`Invalid JSON: ${body}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Helper function for health check
async function healthCheck() {
  return new Promise((resolve, reject) => {
    const req = http.get(HEALTH_ENDPOINT, (res) => {
      let body = '';
      
      res.on('data', (chunk) => {
        body += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          resolve({
            status: res.statusCode,
            data: result,
          });
        } catch (error) {
          reject(new Error(`Invalid JSON: ${body}`));
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(5000, () => {
      reject(new Error('Health check timeout'));
    });
  });
}

describe('Apollo Federation Gateway', () => {
  
  beforeAll(async () => {
    // Wait for gateway to be ready
    let attempts = 0;
    const maxAttempts = 10;
    
    while (attempts < maxAttempts) {
      try {
        const health = await healthCheck();
        if (health.status === 200) {
          break;
        }
      } catch (error) {
        attempts++;
        if (attempts >= maxAttempts) {
          throw new Error('Gateway not ready after maximum attempts');
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  });

  describe('Health Check', () => {
    test('should return healthy status', async () => {
      const response = await healthCheck();
      
      expect(response.status).toBe(200);
      expect(response.data).toMatchObject({
        status: 'ok',
        service: 'apollo-gateway',
        environment: 'development',
      });
      expect(response.data.timestamp).toBeDefined();
    });
  });

  describe('Schema Introspection', () => {
    test('should return federated schema with types from all services', async () => {
      const query = `
        query IntrospectSchema {
          __schema {
            types {
              name
              kind
            }
          }
        }
      `;

      const response = await graphqlRequest(query);
      
      expect(response.status).toBe(200);
      expect(response.data.errors).toBeUndefined();
      expect(response.data.data).toBeDefined();
      
      const typeNames = response.data.data.__schema.types.map(type => type.name);
      
      // Check that types from user-management are present
      expect(typeNames).toContain('UserType');
      expect(typeNames).toContain('UserListResponse');
      expect(typeNames).toContain('CreateUserInput');
      
      // Check that types from calorie-balance are present
      expect(typeNames).toContain('UcalorieUbalanceType');
      expect(typeNames).toContain('UcalorieUbalanceListResponse');
      expect(typeNames).toContain('CreateUcalorieUbalanceInput');
    });
  });

  describe('Cross-Service Queries', () => {
    test('should execute federated query across multiple services', async () => {
      const query = `
        query FederatedQuery {
          listUsers(limit: 1) {
            success
            message
            data {
              id
              email
              username
            }
          }
          listCalorieBalances(limit: 1) {
            success
            message
            data {
              id
              name
              description
            }
          }
        }
      `;

      const response = await graphqlRequest(query);
      
      expect(response.status).toBe(200);
      expect(response.data.errors).toBeUndefined();
      expect(response.data.data).toBeDefined();
      
      // Check user-management response structure
      expect(response.data.data.listUsers).toMatchObject({
        success: expect.any(Boolean),
        message: expect.any(String),
        data: expect.any(Array),
      });
      
      // Check calorie-balance response structure
      expect(response.data.data.listCalorieBalances).toMatchObject({
        success: expect.any(Boolean),
        message: expect.any(String),
        data: expect.any(Array),
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle invalid queries gracefully', async () => {
      const query = `
        query InvalidQuery {
          nonExistentField
        }
      `;

      const response = await graphqlRequest(query);
      
      expect(response.status).toBe(200); // GraphQL returns 200 with errors in body
      expect(response.data.errors).toBeDefined();
      expect(response.data.errors).toHaveLength(1);
      expect(response.data.errors[0].message).toContain('nonExistentField');
    });

    test('should handle malformed queries', async () => {
      const query = `
        query MalformedQuery {
          listUsers {
            // Missing closing brace
      `;

      const response = await graphqlRequest(query);
      
      expect(response.status).toBe(400); // Bad request for syntax errors
    });
  });

  describe('Performance', () => {
    test('should respond to queries within acceptable time', async () => {
      const query = `
        query PerformanceTest {
          listUsers(limit: 5) {
            success
            data {
              id
              email
            }
          }
        }
      `;

      const startTime = Date.now();
      const response = await graphqlRequest(query);
      const endTime = Date.now();
      
      const responseTime = endTime - startTime;
      
      expect(response.status).toBe(200);
      expect(response.data.errors).toBeUndefined();
      expect(responseTime).toBeLessThan(2000); // Should respond within 2 seconds
    });
  });
});