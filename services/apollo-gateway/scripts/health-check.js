#!/usr/bin/env node
/**
 * Health Check Script for Apollo Gateway
 * Verifies that the gateway is running and all subgraphs are accessible
 */

import http from 'http';
import { logger } from '../src/utils/logger.js';

const GATEWAY_URL = process.env.GATEWAY_URL || 'http://localhost:4000';
const HEALTH_ENDPOINT = `${GATEWAY_URL}/health`;

async function checkHealth(url) {
  return new Promise((resolve, reject) => {
    const request = http.get(url, (response) => {
      let data = '';
      
      response.on('data', chunk => {
        data += chunk;
      });
      
      response.on('end', () => {
        try {
          const result = JSON.parse(data);
          resolve({
            status: response.statusCode,
            data: result
          });
        } catch (error) {
          reject(new Error(`Invalid JSON response: ${data}`));
        }
      });
    });
    
    request.on('error', reject);
    request.setTimeout(5000, () => {
      reject(new Error('Request timeout'));
    });
  });
}

async function performHealthCheck() {
  try {
    console.log('🏥 Checking Apollo Gateway health...');
    console.log(`📍 Endpoint: ${HEALTH_ENDPOINT}`);
    
    const result = await checkHealth(HEALTH_ENDPOINT);
    
    if (result.status === 200) {
      console.log('✅ Health check passed!');
      console.log('📊 Gateway Status:', JSON.stringify(result.data, null, 2));
      process.exit(0);
    } else {
      console.error('❌ Health check failed!');
      console.error('Status:', result.status);
      console.error('Response:', result.data);
      process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ Health check failed with error:');
    console.error(error.message);
    process.exit(1);
  }
}

performHealthCheck();