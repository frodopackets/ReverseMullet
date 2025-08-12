#!/usr/bin/env node

/**
 * Test script to verify the router UI integration
 * This tests the frontend components and message handling
 */

const fs = require('fs');
const path = require('path');

console.log('=== Router UI Integration Test ===\n');

// Test 1: Verify component files exist
console.log('1. Checking component files...');
const componentFiles = [
  'src/components/chat/agent-indicator.tsx',
  'src/components/chat/agent-loading-state.tsx',
  'src/components/chat/simple-chat-interface.tsx',
  'src/components/chat/status-indicator.tsx'
];

let allFilesExist = true;
componentFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`✓ ${file} exists`);
  } else {
    console.log(`✗ ${file} missing`);
    allFilesExist = false;
  }
});

// Test 2: Verify main page component updates
console.log('\n2. Checking main page component updates...');
const mainPagePath = path.join(__dirname, 'src/app/page.tsx');
if (fs.existsSync(mainPagePath)) {
  const mainPageContent = fs.readFileSync(mainPagePath, 'utf8');
  
  const checks = [
    { name: 'Router endpoint usage', pattern: /router-chat/ },
    { name: 'Loading stage state', pattern: /loadingStage/ },
    { name: 'Current agent state', pattern: /currentAgent/ },
    { name: 'Agent metadata handling', pattern: /agent_type/ },
    { name: 'Intent analysis handling', pattern: /intent_analysis/ },
    { name: 'Updated title', pattern: /Intelligent AWS Assistant/ }
  ];
  
  checks.forEach(check => {
    if (check.pattern.test(mainPageContent)) {
      console.log(`✓ ${check.name} implemented`);
    } else {
      console.log(`✗ ${check.name} missing`);
      allFilesExist = false;
    }
  });
} else {
  console.log('✗ Main page component not found');
  allFilesExist = false;
}

// Test 3: Verify Message interface updates
console.log('\n3. Checking Message interface updates...');
const chatInterfacePath = path.join(__dirname, 'src/components/chat/simple-chat-interface.tsx');
if (fs.existsSync(chatInterfacePath)) {
  const chatContent = fs.readFileSync(chatInterfacePath, 'utf8');
  
  const interfaceChecks = [
    { name: 'Agent type field', pattern: /agent_type\?:/ },
    { name: 'Intent analysis field', pattern: /intent_analysis\?:/ },
    { name: 'Orchestration metadata field', pattern: /orchestration_metadata\?:/ },
    { name: 'Agent indicator import', pattern: /import.*AgentIndicator/ },
    { name: 'Agent loading state import', pattern: /import.*AgentLoadingState/ }
  ];
  
  interfaceChecks.forEach(check => {
    if (check.pattern.test(chatContent)) {
      console.log(`✓ ${check.name} implemented`);
    } else {
      console.log(`✗ ${check.name} missing`);
      allFilesExist = false;
    }
  });
} else {
  console.log('✗ Chat interface component not found');
  allFilesExist = false;
}

// Test 4: Verify infrastructure updates
console.log('\n4. Checking infrastructure updates...');
const infraPath = path.join(__dirname, 'aws-infrastructure.yaml');
if (fs.existsSync(infraPath)) {
  const infraContent = fs.readFileSync(infraPath, 'utf8');
  
  const infraChecks = [
    { name: 'Router Lambda function', pattern: /RouterChatLambdaFunction/ },
    { name: 'Router API resource', pattern: /RouterChatResource/ },
    { name: 'Router POST method', pattern: /RouterChatPostMethod/ },
    { name: 'Router endpoint output', pattern: /RouterChatEndpoint/ }
  ];
  
  infraChecks.forEach(check => {
    if (check.pattern.test(infraContent)) {
      console.log(`✓ ${check.name} configured`);
    } else {
      console.log(`✗ ${check.name} missing`);
      allFilesExist = false;
    }
  });
} else {
  console.log('✗ Infrastructure file not found');
  allFilesExist = false;
}

// Test 5: Check for service selector removal
console.log('\n5. Checking for service selector removal...');
const srcDir = path.join(__dirname, 'src');
let serviceSelectorFound = false;

function searchForServiceSelector(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory() && !file.startsWith('.')) {
      searchForServiceSelector(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      const content = fs.readFileSync(filePath, 'utf8');
      if (/service.*select|selector.*service/i.test(content) && !content.includes('service selection UI')) {
        console.log(`? Potential service selector found in ${filePath}`);
        serviceSelectorFound = true;
      }
    }
  });
}

if (fs.existsSync(srcDir)) {
  searchForServiceSelector(srcDir);
  if (!serviceSelectorFound) {
    console.log('✓ No service selector components found (as expected)');
  }
} else {
  console.log('✗ Source directory not found');
  allFilesExist = false;
}

// Summary
console.log('\n=== Test Summary ===');
if (allFilesExist && !serviceSelectorFound) {
  console.log('✅ All router UI integration tests passed!');
  console.log('\nNext steps:');
  console.log('1. Build and test the frontend: npm run build');
  console.log('2. Deploy the updated infrastructure with router endpoint');
  console.log('3. Test the router agent functionality end-to-end');
  process.exit(0);
} else {
  console.log('❌ Some tests failed. Please review the issues above.');
  process.exit(1);
}