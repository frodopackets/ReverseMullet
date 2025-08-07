// Test script to verify static export configuration
const fs = require('fs');
const path = require('path');

console.log('🧪 Testing Static Export Configuration');
console.log('=====================================');

// Check Next.js config
console.log('\n1. Checking Next.js configuration...');
if (fs.existsSync('next.config.ts')) {
  const config = fs.readFileSync('next.config.ts', 'utf8');
  if (config.includes("output: 'export'")) {
    console.log('✅ Static export enabled');
  } else {
    console.log('❌ Static export not configured');
  }
} else {
  console.log('❌ next.config.ts not found');
}

// Check for API routes (should not exist)
console.log('\n2. Checking for API routes...');
if (fs.existsSync('src/app/api')) {
  console.log('❌ API routes found - these will cause static export to fail');
  console.log('   Please remove the src/app/api directory');
} else {
  console.log('✅ No API routes found - good for static export');
}

// Check mock API
console.log('\n3. Checking mock API...');
if (fs.existsSync('src/lib/mock-api.ts')) {
  console.log('✅ Mock API found');
} else {
  console.log('❌ Mock API not found');
}

// Check pages
console.log('\n4. Checking pages...');
const pages = ['src/app/page.tsx', 'src/app/terminal/page.tsx', 'src/app/bubblegum/page.tsx'];
pages.forEach(page => {
  if (fs.existsSync(page)) {
    console.log(`✅ ${page} exists`);
  } else {
    console.log(`❌ ${page} missing`);
  }
});

console.log('\n🎯 Static Export Status:');
const hasApiRoutes = fs.existsSync('src/app/api');
const hasStaticConfig = fs.existsSync('next.config.ts') && 
  fs.readFileSync('next.config.ts', 'utf8').includes("output: 'export'");

if (!hasApiRoutes && hasStaticConfig) {
  console.log('✅ Ready for static export!');
} else {
  console.log('❌ Not ready for static export');
  if (hasApiRoutes) console.log('   - Remove API routes');
  if (!hasStaticConfig) console.log('   - Configure static export in next.config.ts');
}