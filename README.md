# Mastercontrol MCP

An MCP server for the Mastercontrol Document Management System (mastercontrol.com). If you don't know what it is, you don't need it. But if you do know what it is, and you want an easier way to programmatically extract documents than via its...ehm...interesting user interface, then this is for you!

## Features

- **Retrieve metadata**: Get infocard information
- **Get file name and contents**: Get the file as original or PDF, with Base64 file data
- **Download file**: Save to your drive in a specified sandbox folder

## Installation

### Get your Mastercontrol API key

Refer to the pages 
https://[tenant].mastercontrol.com/[tenant]/static/swagger/index.html
https://[tenant].mastercontrol.com/[tenant]/index.cfm#/api-module/api-key

Where [tenant] is the name of your company. Peek at the browser address bar when you're in the UI of Mastercontrol to find out.

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/morsm/mastercontrol-mcp.git
cd mastercontrol-mcp

# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

Start the MCP server:

```bash
startServer.sh --tenant mycompany --key mykey --data-dir /Users/me/Agents/files
```

Configuration for Claude Desktop:
```claude_desktop_config.json
    "mastercontrol-mcp": {
      "command": "/Users/me/Agents/servers/mastercontrol-mcp/startServer.sh",
      "args": ["--tenant", "mycompany", "--key", "mykey", "--data-dir", "/Users/me/Agents/files"],
      "cwd": "/Users/me/Agents/servers/mastercontrol-mcp"
    } 
```

## Development

- Python 3.12+ required
- Uses the MCP framework for tool registration

```bash
# Update dependencies
uv pip install -e . --upgrade

# Commit changes (uses conventional commit format)
cz commit
```

## Dependencies

- [MCP Framework](https://github.com/modelcontextprotocol/python-sdk)

## License

MIT. See [LICENSE](LICENSE).
