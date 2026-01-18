#!/usr/bin/env node
/**
 * Elite+ Wrapper for Flask Integration
 * 
 * This script provides a command-line interface to the SIRCL encoder
 * for use with Flask backend via subprocess.
 */

import { SIRCLEncoder } from './sircl.js';

// Read input from stdin
let inputData = '';
process.stdin.setEncoding('utf8');

process.stdin.on('data', (chunk) => {
  inputData += chunk;
});

process.stdin.on('end', () => {
  try {
    const data = JSON.parse(inputData);
    const code = data.code || '';
    const config = data.config || {};
    
    if (!code) {
      process.stdout.write(JSON.stringify({
        error: 'No code provided'
      }));
      process.exit(1);
    }
    
    // Create encoder with config
    const encoder = new SIRCLEncoder({
      enableSemanticEncoding: config.enableSemanticEncoding !== false,
      enableRepetitionCompression: config.enableRepetitionCompression !== false,
      preserveControlFlow: config.preserveControlFlow !== false,
      preserveVerbs: config.preserveVerbs !== false,
      hybridEncoding: config.hybridEncoding !== false,
      crossFileStable: config.crossFileStable !== false,
      minLengthForUnicode: config.minLengthForUnicode || 6,
      minFrequency: config.minFrequency || 3,
      minNetSavings: config.minNetSavings || 10,
      macroMinOccurrences: config.macroMinOccurrences || 2,
      maxMacros: config.maxMacros || 26
    });
    
    // Encode the code
    const result = encoder.encodeFile(code, data.filePath || '');
    
    // Return result as JSON
    process.stdout.write(JSON.stringify({
      code: result.code,
      metadata: result.metadata,
      success: true
    }));
    
  } catch (error) {
    process.stdout.write(JSON.stringify({
      error: error.message,
      stack: error.stack,
      success: false
    }));
    process.exit(1);
  }
});
