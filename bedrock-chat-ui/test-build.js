// Simple test to verify Next.js configuration
const fs = require('fs');
const path = require('path');

console.log('🔍 Checking Next.js configuration...');

// Check if next.config.ts exists and has static export
const configPath = path.join(__dirname, 'next.config.ts');
if (fs.existsSync(configPath)) {
  const config = fs.readFileSync(configPath, 'utf8');
  if (config.includes("output: 'export'")) {
    console.log('✅ Next.js configured for static export');
  } else {
    console.log('❌ Static export not configured');
  }
} else {
  console.log('❌ next.config.ts not found');
}

// Check if amplify.yml exists
const amplifyPath = path.join(__dirname, 'amplify.yml');
if (fs.existsSync(amplifyPath)) {
  console.log('✅ Amplify build configuration found');
} else {
  console.log('❌ amplify.yml not found');
}

// Check package.json scripts
const packagePath = path.join(__dirname, 'package.json');
if (fs.existsSync(packagePath)) {
  const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  if (pkg.scripts && pkg.scripts.build) {
    console.log('✅ Build script configured');
  } else {
    console.log('❌ Build script missing');
  }
}

console.log('\n🚀 Configuration check complete!');
console.log('\nNext steps:');
console.log('1. Push your code to GitHub');
console.log('2. Go to AWS Amplify Console');
console.log('3. Connect your GitHub repository');
console.log('4. Deploy your app');