# Environment Command Guidelines

## Development Environment Context

The development environment is running on Windows 11 with Kiro installed locally, but all development work is performed in a WSL (Ubuntu) environment with Python virtual environments.

## Command Execution Guidelines

### Shell Command Pattern
Always use the `bash -l -c` pattern when executing commands to ensure proper environment loading:

```
bash -l -c "cd project-directory && command"
```

### Python Environment
- All Python commands should assume a virtual environment is active
- Use `python` and `pip` commands directly (not `python3` or `pip3`)
- Always change to the project directory first before running Python commands

### Example Command Patterns

#### Installing Python packages:
```
bash -l -c "cd bedrock-chat-ui && source venv/bin/activate && pip install package-name"
```

#### Running Python scripts:
```
bash -l -c "cd bedrock-chat-ui && source venv/bin/activate && python script.py"
```

#### Node.js/npm commands:
```
bash -l -c "cd bedrock-chat-ui && npm install"
bash -l -c "cd bedrock-chat-ui && npm run dev"
```

#### File operations that need environment context:
```
bash -l -c "cd bedrock-chat-ui && ls -la"
bash -l -c "cd bedrock-chat-ui && mkdir new-directory"
```

### Directory Structure Awareness
- Main project directory: `/home/robww/ReverseMullet`
- Chat UI project: `/home/robww/ReverseMullet/bedrock-chat-ui`
- Always use relative paths from the main project directory when possible

### Virtual Environment Considerations
- **IMPORTANT**: A Python virtual environment already exists at `bedrock-chat-ui/venv/`
- **ALWAYS activate the venv** when running Python commands: `source venv/bin/activate`
- The venv contains all required dependencies including `strands-agents` and `mcp`
- Use standard `python` and `pip` commands (not `python3` or `pip3`) after activation
- Don't attempt to create new virtual environments - use the existing one

## Implementation Notes for AWS Pricing Agent

When implementing the AWS Pricing Agent:

1. **Python package installations**: Use `bash -l -c "cd bedrock-chat-ui && source venv/bin/activate && pip install package-name"`
2. **Node.js dependencies**: Use `bash -l -c "cd bedrock-chat-ui && npm install package-name"`
3. **File operations**: Always change to appropriate directory first
4. **Testing commands**: Use `bash -l -c "cd bedrock-chat-ui && source venv/bin/activate && python -m pytest"` or similar
5. **Running agent scripts**: Use `bash -l -c "cd bedrock-chat-ui && source venv/bin/activate && python script.py"`

This ensures consistent execution in the WSL Ubuntu environment with proper virtual environment and path handling.

## Virtual Environment Status
- **Location**: `bedrock-chat-ui/venv/`
- **Status**: Already created and configured
- **Dependencies**: Contains `strands-agents`, `mcp`, and all required packages
- **Activation**: Always use `source venv/bin/activate` before Python commands