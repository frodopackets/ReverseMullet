# WSL Command Execution Guidelines

## Problem
When using PowerShell to execute WSL commands, `wsl command` starts a fresh session without the user's environment, PATH, or installed tools.

## Solution
Always use bash login shell for WSL commands to inherit the user's full environment:

```bash
wsl bash -l -c "command"
```

## Examples

**❌ Wrong (will fail if tool not in system PATH):**
```bash
wsl terraform --version
wsl npm --version
wsl docker --version
```

**✅ Correct (inherits user environment):**
```bash
wsl bash -l -c "terraform --version"
wsl bash -l -c "npm --version" 
wsl bash -l -c "docker --version"
```

## Usage Pattern
For any WSL command execution, always wrap with `bash -l -c "..."` to ensure:
- User's PATH is loaded
- Environment variables are available
- Installed tools are accessible
- Shell configuration is applied

This is especially important for:
- Development tools (terraform, docker, node, etc.)
- User-installed binaries
- Commands that depend on environment setup