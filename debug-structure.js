// Debug script to check repository structure
const fs = require('fs');
const path = require('path');

console.log('🔍 Repository Structure Debug');
console.log('============================');

// Check current directory
console.log('Current directory:', process.cwd());

// List root directory contents
console.log('\nRoot directory contents:');
try {
  const rootContents = fs.readdirSync('.');
  rootContents.forEach(item => {
    const stats = fs.statSync(item);
    console.log(`${stats.isDirectory() ? '📁' : '📄'} ${item}`);
  });
} catch (error) {
  console.log('❌ Error reading root directory:', error.message);
}

// Check if bedrock-chat-ui exists
console.log('\nChecking bedrock-chat-ui directory:');
if (fs.existsSync('bedrock-chat-ui')) {
  console.log('✅ bedrock-chat-ui directory exists');
  
  // Check for package.json
  if (fs.existsSync('bedrock-chat-ui/package.json')) {
    console.log('✅ package.json found in bedrock-chat-ui');
    
    // Read package.json
    try {
      const pkg = JSON.parse(fs.readFileSync('bedrock-chat-ui/package.json', 'utf8'));
      console.log('📦 App name:', pkg.name);
      console.log('📦 Scripts:', Object.keys(pkg.scripts || {}));
    } catch (error) {
      console.log('❌ Error reading package.json:', error.message);
    }
  } else {
    console.log('❌ package.json NOT found in bedrock-chat-ui');
  }
  
  // Check for amplify.yml
  if (fs.existsSync('bedrock-chat-ui/amplify.yml')) {
    console.log('✅ amplify.yml found in bedrock-chat-ui');
  } else {
    console.log('⚠️  amplify.yml NOT found in bedrock-chat-ui');
  }
} else {
  console.log('❌ bedrock-chat-ui directory does NOT exist');
}

// Check for root amplify.yml
if (fs.existsSync('amplify.yml')) {
  console.log('✅ amplify.yml found in root');
} else {
  console.log('❌ amplify.yml NOT found in root');
}

console.log('\n🎯 Recommendations:');
console.log('1. Make sure bedrock-chat-ui folder exists in your repository');
console.log('2. Ensure package.json is in bedrock-chat-ui/package.json');
console.log('3. Use the monorepo configuration in amplify.yml');
console.log('4. Or set "App root directory" to "bedrock-chat-ui" in Amplify Console');