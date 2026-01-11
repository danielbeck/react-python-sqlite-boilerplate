#!/usr/bin/env node
/**
 * Generate frontend config from root config.json
 * This should be run before building the frontend
 */


import fs from 'fs';
import path from 'path';

// Read root config.json

const __dirname = path.dirname(new URL(import.meta.url).pathname);
const rootConfigPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(rootConfigPath, 'utf8'));

// Extract relevant frontend config
let subDir = config.deployment.subDir || '';
// normalize: remove any leading/trailing slashes so we can assemble paths predictably
subDir = subDir.replace(/^\/+|\/+$/g, '');
const domain = config.production.domain;

// Generate frontend config
const frontendConfig = {
    API_BASE_PATH: subDir ? `/${subDir}/backend/api.cgi` : '/backend/api.cgi',
    BASE_URL: subDir ? `/${subDir}/` : '/',
};

// Write to frontend/src/config.js
const configContent = `// Auto-generated from config.json - DO NOT EDIT MANUALLY
// Run 'npm run generate-config' to regenerate

export const config = ${JSON.stringify(frontendConfig, null, 2)};
`;


const outputPath = path.join(__dirname, 'src', 'config.js');
fs.writeFileSync(outputPath, configContent);

console.log('✅ Frontend config generated:', outputPath);
console.log('   API_BASE_PATH:', frontendConfig.API_BASE_PATH);
console.log('   BASE_URL:', frontendConfig.BASE_URL);
