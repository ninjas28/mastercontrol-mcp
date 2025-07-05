import argparse
import logging
from mcp.server.fastmcp import FastMCP
from mastercontrol import MasterControl

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="MasterControl MCP Server")
    parser.add_argument("--key", required=True, help="MasterControl API Key")
    parser.add_argument("--tenant", required=True, help="MasterControl Tenant")
    parser.add_argument("--data-dir", required=True, help="Directory to store downloaded files")
    args = parser.parse_args()

    mc = MasterControl(args.key, args.tenant, args.data_dir)
    mcp = FastMCP("mastercontrol-mcp", key=args.key, tenant=args.tenant, data_dir=args.data_dir)

    mcp.add_tool(mc.get_infocard)
    mcp.add_tool(mc.get_file_from_infocard)
    mcp.add_tool(mc.get_file_and_infocard)
    mcp.add_tool(mc.get_file)
    mcp.add_tool(mc.download_file)

    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
