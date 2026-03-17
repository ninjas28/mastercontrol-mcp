# Mastercontrol MCP

An MCP server for the Mastercontrol Document Management System (mastercontrol.com). If you don't know what it is, you don't need it. But if you do know what it is, and you want an easier way to programmatically extract documents than via its...ehm...interesting user interface, then this is for you!

## Features

### Documents
- **Infocard metadata**: Get infocard by document number or infocard ID, with extended details
- **Revision navigation**: Get latest, released, next, or previous revision infocards
- **Access rights**: Check user find rights and anonymous vault rights
- **Main file retrieval**: Download main file (original or PDF) as Base64, or save to disk
- **Published file variants**: Get published, altered-published, or modified-published PDFs as Base64
- **File existence checks**: Check whether main, encrypted, or published main files exist
- **Attachments**: List attachments or download a specific attachment as Base64
- **Document links**: Get linked documents and their metadata

### Document Types & Configuration
- **Document types**: List all types, download templates, check if an infocard is a type
- **Custom fields per type/subtype**: Get configured custom fields for types and subtypes
- **Subtypes**: List subtypes under a parent document type
- **Document settings**: Get global tenant document settings
- **Vault change search**: Search for documents whose vault has changed, with date filtering and pagination

### Custom Fields
- **Portal custom fields**: List all custom fields and options for custom data fields
- **Field values by revision**: Get custom field values for a document revision
- **Field values by infocard ID**: Get all custom field values for a document

### Data Structures
- **List structures**: List all data structures or checklist data structures
- **Retrieve rows**: Get all rows, filtered rows, or a single row from a data structure
- **Paginated access**: Page through large data structures with optional type/query filters
- **Metadata**: Get access rights, total row count, or the next auto-generated number

### Folders / Explorer
- **Root folder tree**: Get the top-level document explorer structure
- **Taxonomy folders**: Browse taxonomy folder contents by ID and path
- **Static & virtual folders**: Get contents of static or virtual folders
- **Export**: Export a folder as a downloadable archive (Base64)

### Forms
- **Form metadata**: Get form infocard by form number/revision or infocard ID
- **Attachments & links**: List attachments, download attachments, get linked documents and metadata
- **Web links**: Get web links attached to a form
- **Workflows**: List all or only enabled form workflow definitions
- **Form status**: Get current workflow task/status for a form
- **Published PDFs**: Download modified-published or published infocard PDFs as Base64

### Portal Administration
- **Current user**: Get the authenticated user's profile
- **Application rights**: Query portal application rights with optional filtering and pagination
- **Business units**: List all business units, get a user's business units, get roles per unit
- **Roles**: List all roles, get role members, get a user's roles or interactable roles
- **Vaults**: List all vaults and get publishing settings per vault
- **Lifecycles**: List all document lifecycle definitions
- **Coversheets**: List available publishing coversheets

### Suppliers & Registrations
- **Suppliers**: List all suppliers, get a specific supplier, and list their supplied items
- **Supplied items**: List all supplied items and get their associated suppliers
- **Registrations**: List all registrations or get a specific registration

### SCIM & Licenses
- **SCIM users**: List or get users via the SCIM v0 API, with filtering and pagination
- **Third-party licenses**: Retrieve open-source license information used by MasterControl

## Installation

### Get your Mastercontrol API key

Refer to the pages 
https://[tenant].mastercontrol.com/[tenant]/static/swagger/index.html
https://[tenant].mastercontrol.com/[tenant]/index.cfm#/api-module/api-key

Where [tenant] is the name of your company. Peek at the browser address bar when you're in the UI of Mastercontrol to find out.

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/ninjas28/mastercontrol-mcp.git
cd mastercontrol-mcp

# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

Start the MCP server:

```bash
uv run server.py --tenant mycompany --key mykey --data-dir /Users/me/Agents/files
```

Configuration for Claude Desktop:
```json
    "mastercontrol-mcp": {
      "command": "uv",
      "args": ["run", "server.py", "--tenant", "mycompany", "--key", "mykey", "--data-dir", "/Users/me/Agents/files"],
      "cwd": "/Users/me/Agents/servers/mastercontrol-mcp"
    }
```
For other configurations, start the MCP server and then setup a streamable-http connection from your LLM to the server at /mcp.

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
