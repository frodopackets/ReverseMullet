#!/usr/bin/env node

/**
 * Test script to validate Terraform configuration for router endpoint
 */

const fs = require('fs');
const path = require('path');

console.log('=== Terraform Router Configuration Test ===\n');

// Test 1: Verify Terraform file exists and is readable
console.log('1. Checking Terraform configuration...');
const terraformPath = path.join(__dirname, 'terraform/main.tf');
if (!fs.existsSync(terraformPath)) {
  console.log('✗ Terraform main.tf not found');
  process.exit(1);
}

const terraformContent = fs.readFileSync(terraformPath, 'utf8');
console.log('✓ Terraform main.tf found and readable');

// Test 2: Verify router Lambda function configuration
console.log('\n2. Checking router Lambda function configuration...');
const lambdaChecks = [
  { name: 'Router Lambda function resource', pattern: /resource "aws_lambda_function" "router_chat_function"/ },
  { name: 'Router Lambda handler', pattern: /handler\s*=\s*"router-chat-handler\.handler"/ },
  { name: 'Router Lambda function name', pattern: /function_name\s*=\s*"\$\{var\.project_name\}-router-chat-\$\{var\.environment\}"/ },
  { name: 'Router Lambda timeout', pattern: /timeout\s*=\s*30/ }
];

let allLambdaChecks = true;
lambdaChecks.forEach(check => {
  if (check.pattern.test(terraformContent)) {
    console.log(`✓ ${check.name} configured`);
  } else {
    console.log(`✗ ${check.name} missing`);
    allLambdaChecks = false;
  }
});

// Test 3: Verify API Gateway resources
console.log('\n3. Checking API Gateway resources...');
const apiGatewayChecks = [
  { name: 'Router chat resource', pattern: /resource "aws_api_gateway_resource" "router_chat_resource"/ },
  { name: 'Router chat path part', pattern: /path_part\s*=\s*"router-chat"/ },
  { name: 'Router chat POST method', pattern: /resource "aws_api_gateway_method" "router_chat_post"/ },
  { name: 'Router chat OPTIONS method', pattern: /resource "aws_api_gateway_method" "router_chat_options"/ },
  { name: 'Router chat POST integration', pattern: /resource "aws_api_gateway_integration" "router_chat_post_integration"/ },
  { name: 'Router chat OPTIONS integration', pattern: /resource "aws_api_gateway_integration" "router_chat_options_integration"/ }
];

let allApiGatewayChecks = true;
apiGatewayChecks.forEach(check => {
  if (check.pattern.test(terraformContent)) {
    console.log(`✓ ${check.name} configured`);
  } else {
    console.log(`✗ ${check.name} missing`);
    allApiGatewayChecks = false;
  }
});

// Test 4: Verify CORS configuration
console.log('\n4. Checking CORS configuration...');
const corsChecks = [
  { name: 'Router OPTIONS method response', pattern: /resource "aws_api_gateway_method_response" "router_chat_options_response"/ },
  { name: 'Router OPTIONS integration response', pattern: /resource "aws_api_gateway_integration_response" "router_chat_options_integration_response"/ },
  { name: 'CORS headers configuration', pattern: /"method\.response\.header\.Access-Control-Allow-Headers"/ },
  { name: 'CORS methods configuration', pattern: /"method\.response\.header\.Access-Control-Allow-Methods"/ },
  { name: 'CORS origin configuration', pattern: /"method\.response\.header\.Access-Control-Allow-Origin"/ }
];

let allCorsChecks = true;
corsChecks.forEach(check => {
  if (check.pattern.test(terraformContent)) {
    console.log(`✓ ${check.name} configured`);
  } else {
    console.log(`✗ ${check.name} missing`);
    allCorsChecks = false;
  }
});

// Test 5: Verify Lambda permissions
console.log('\n5. Checking Lambda permissions...');
const permissionChecks = [
  { name: 'Router Lambda API Gateway permission', pattern: /resource "aws_lambda_permission" "router_chat_api_gateway"/ },
  { name: 'Router Lambda function name reference', pattern: /function_name\s*=\s*aws_lambda_function\.router_chat_function\.function_name/ }
];

let allPermissionChecks = true;
permissionChecks.forEach(check => {
  if (check.pattern.test(terraformContent)) {
    console.log(`✓ ${check.name} configured`);
  } else {
    console.log(`✗ ${check.name} missing`);
    allPermissionChecks = false;
  }
});

// Test 6: Verify deployment dependencies
console.log('\n6. Checking deployment dependencies...');
const deploymentChecks = [
  { name: 'Router POST method in dependencies', pattern: /aws_api_gateway_method\.router_chat_post/ },
  { name: 'Router OPTIONS method in dependencies', pattern: /aws_api_gateway_method\.router_chat_options/ },
  { name: 'Router POST integration in dependencies', pattern: /aws_api_gateway_integration\.router_chat_post_integration/ },
  { name: 'Router OPTIONS integration in dependencies', pattern: /aws_api_gateway_integration\.router_chat_options_integration/ },
  { name: 'Router integration in triggers', pattern: /router_chat_post_integration\.content_handling/ }
];

let allDeploymentChecks = true;
deploymentChecks.forEach(check => {
  if (check.pattern.test(terraformContent)) {
    console.log(`✓ ${check.name} configured`);
  } else {
    console.log(`✗ ${check.name} missing`);
    allDeploymentChecks = false;
  }
});

// Test 7: Verify outputs
console.log('\n7. Checking outputs...');
const outputChecks = [
  { name: 'Router chat endpoint output', pattern: /output "router_chat_endpoint"/ },
  { name: 'Router endpoint URL format', pattern: /router-chat/ }
];

let allOutputChecks = true;
outputChecks.forEach(check => {
  if (check.pattern.test(terraformContent)) {
    console.log(`✓ ${check.name} configured`);
  } else {
    console.log(`✗ ${check.name} missing`);
    allOutputChecks = false;
  }
});

// Test 8: Verify Lambda handler file exists
console.log('\n8. Checking Lambda handler file...');
const handlerPath = path.join(__dirname, 'lambda/router-chat-handler.js');
if (fs.existsSync(handlerPath)) {
  console.log('✓ Router chat handler file exists');
} else {
  console.log('✗ Router chat handler file missing');
  console.log('  Note: This is expected if the handler hasn\'t been deployed yet');
}

// Summary
console.log('\n=== Test Summary ===');
const allTestsPassed = allLambdaChecks && allApiGatewayChecks && allCorsChecks && 
                      allPermissionChecks && allDeploymentChecks && allOutputChecks;

if (allTestsPassed) {
  console.log('✅ All Terraform router configuration tests passed!');
  console.log('\nNext steps:');
  console.log('1. Run terraform plan to validate configuration');
  console.log('2. Run terraform apply to deploy router endpoint');
  console.log('3. Test the router endpoint functionality');
  console.log('\nCommands:');
  console.log('  cd terraform');
  console.log('  terraform plan');
  console.log('  terraform apply');
  process.exit(0);
} else {
  console.log('❌ Some Terraform configuration tests failed.');
  console.log('Please review the issues above before deploying.');
  process.exit(1);
}