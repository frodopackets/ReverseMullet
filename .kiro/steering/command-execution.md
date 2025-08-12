---
inclusion: always
---

# Command Execution Guidelines

## CRITICAL: Always Use WSL Environment

You are working on a Windows 11 system with development in WSL (Ubuntu). **ALL commands must use the `bash -l -c` pattern**.

### Required Command Format
```
bash -l -c "cd target-directory && your-command"
```

### Project Structure
- Main project: `/home/robww/ReverseMullet`
- Chat UI: `/home/robww/ReverseMullet/bedrock-chat-ui`

### Common Commands

#### Python/pip (with venv active):
```
bash -l -c "cd bedrock-chat-ui && source venv/bin/activate && pip install strands-agents"
bash -l -c "cd bedrock-chat-ui && source venv/bin/activate && python script.py"
```

#### Node.js/npm:
```
bash -l -c "cd bedrock-chat-ui && npm install package-name"
bash -l -c "cd bedrock-chat-ui && npm run dev"
```

#### File operations:
```
bash -l -c "cd bedrock-chat-ui && mkdir src/agents"
bash -l -c "cd bedrock-chat-ui && ls -la src/"
```

### DO NOT USE:
- Direct PowerShell commands for development tasks
- Commands without `bash -l -c` wrapper
- Commands without proper directory navigation

### ALWAYS USE:
- `bash -l -c "cd appropriate-directory && command"`
- Proper directory context before running commands
- Standard `python` and `pip` (not `python3` or `pip3`)
- **Virtual environment activation**: `source venv/bin/activate` for Python commands

### VIRTUAL ENVIRONMENT:
- **Location**: `bedrock-chat-ui/venv/` (already exists)
- **Required for**: All Python commands and package installations
- **Activation**: Always include `source venv/bin/activate` before Python commands