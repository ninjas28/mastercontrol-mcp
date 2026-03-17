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
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=3000, help="Port to bind the server to")
    args = parser.parse_args()

    mc = MasterControl(args.key, args.tenant, args.data_dir)
    mcp = FastMCP("mastercontrol-mcp", host=args.host, port=args.port)

    # Existing document methods
    mcp.add_tool(mc.get_infocard)
    mcp.add_tool(mc.get_file_from_infocard)
    mcp.add_tool(mc.get_file_and_infocard)
    mcp.add_tool(mc.get_file)
    mcp.add_tool(mc.download_file)

    # Document InfoCard extensions
    mcp.add_tool(mc.get_infocard_by_id)
    mcp.add_tool(mc.get_infocard_details)
    mcp.add_tool(mc.get_latest_revision)
    mcp.add_tool(mc.get_released_revision)
    mcp.add_tool(mc.get_next_revision)
    mcp.add_tool(mc.get_previous_revision)
    mcp.add_tool(mc.has_find_infocard_right)
    mcp.add_tool(mc.get_anonymous_vault_rights)

    # Document file downloads
    mcp.add_tool(mc.get_published_main_file)
    mcp.add_tool(mc.main_file_exists)
    mcp.add_tool(mc.encrypted_main_file_exists)
    mcp.add_tool(mc.published_main_file_exists)
    mcp.add_tool(mc.get_altered_published_pdf)
    mcp.add_tool(mc.get_modified_published_infocard)
    mcp.add_tool(mc.get_published_infocard_pdf)

    # Document attachments & links
    mcp.add_tool(mc.get_attachments)
    mcp.add_tool(mc.get_attachment)
    mcp.add_tool(mc.get_document_links)
    mcp.add_tool(mc.get_document_links_metadata)

    # Document types, settings & vault changes
    mcp.add_tool(mc.get_document_types)
    mcp.add_tool(mc.get_document_type_template)
    mcp.add_tool(mc.is_document_type)
    mcp.add_tool(mc.get_type_custom_fields)
    mcp.add_tool(mc.get_subtype_custom_fields)
    mcp.add_tool(mc.get_subtypes)
    mcp.add_tool(mc.get_document_settings)
    mcp.add_tool(mc.search_vault_changes)

    # Custom fields
    mcp.add_tool(mc.get_custom_fields)
    mcp.add_tool(mc.get_custom_data_field)
    mcp.add_tool(mc.search_custom_fields_by_revision)
    mcp.add_tool(mc.search_custom_fields_by_infocard)

    # Data structures
    mcp.add_tool(mc.get_data_structures)
    mcp.add_tool(mc.get_checklist_data_structures)
    mcp.add_tool(mc.get_checklist_data_structure)
    mcp.add_tool(mc.get_data_structure)
    mcp.add_tool(mc.get_data_structure_paginated)
    mcp.add_tool(mc.get_data_structure_filter_rows)
    mcp.add_tool(mc.get_data_structure_rights)
    mcp.add_tool(mc.get_data_structure_size)
    mcp.add_tool(mc.get_data_structure_row)
    mcp.add_tool(mc.get_next_number)

    # Folders / Explorer
    mcp.add_tool(mc.get_root_folders)
    mcp.add_tool(mc.get_taxonomy_folder)
    mcp.add_tool(mc.export_folder)
    mcp.add_tool(mc.get_static_folder_content)
    mcp.add_tool(mc.get_virtual_folder_content)

    # Forms
    mcp.add_tool(mc.get_form_metadata)
    mcp.add_tool(mc.get_form_by_id)
    mcp.add_tool(mc.get_form_attachments)
    mcp.add_tool(mc.get_form_attachment)
    mcp.add_tool(mc.get_form_links)
    mcp.add_tool(mc.get_form_links_metadata)
    mcp.add_tool(mc.get_form_weblinks)
    mcp.add_tool(mc.get_form_workflows)
    mcp.add_tool(mc.get_enabled_form_workflows)
    mcp.add_tool(mc.get_form_status)
    mcp.add_tool(mc.get_form_modified_published_pdf)
    mcp.add_tool(mc.get_form_published_pdf)

    # Portal admin — users, roles, vaults, business units
    mcp.add_tool(mc.get_current_user)
    mcp.add_tool(mc.get_application_rights)
    mcp.add_tool(mc.get_business_units)
    mcp.add_tool(mc.get_user_business_units)
    mcp.add_tool(mc.get_business_unit_roles)
    mcp.add_tool(mc.get_coversheets)
    mcp.add_tool(mc.get_roles)
    mcp.add_tool(mc.get_role_members)
    mcp.add_tool(mc.get_user_interactable_roles)
    mcp.add_tool(mc.get_user_roles)
    mcp.add_tool(mc.get_vaults)
    mcp.add_tool(mc.get_vault_publishing_settings)
    mcp.add_tool(mc.get_lifecycles)

    # Suppliers, supplied items & registrations
    mcp.add_tool(mc.get_supplied_items)
    mcp.add_tool(mc.get_item_suppliers)
    mcp.add_tool(mc.get_suppliers)
    mcp.add_tool(mc.get_supplier)
    mcp.add_tool(mc.get_supplier_items)
    mcp.add_tool(mc.get_registrations)
    mcp.add_tool(mc.get_registration)

    # SCIM users & open-source licenses
    mcp.add_tool(mc.get_scim_users)
    mcp.add_tool(mc.get_scim_user)
    mcp.add_tool(mc.get_third_party_licenses)
    mcp.add_tool(mc.get_angular_license)

    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
