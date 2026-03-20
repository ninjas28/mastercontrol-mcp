import base64
import http.client
import json
import re
import os
from urllib.parse import urlencode

class MasterControl:
    def __init__(self, key, tenant, data_dir):
        self.key = key
        self.tenant = tenant
        self.data_dir = data_dir
        self.conn = http.client.HTTPSConnection(f"{tenant}.mastercontrol.com")

    def get(self, url, base_path="/v1"):
        self.conn.request("GET", f"/{self.tenant}/restapi{base_path}{url}", headers={'Authorization': f'Bearer {self.key}'})
        res = self.conn.getresponse()
        data = res.read()
        assert res.status == 200
        return data, dict(res.getheaders())

    def _build_url(self, path, params):
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            return f"{path}?{urlencode(filtered)}"
        return path

    # -------------------------------------------------------------------------
    # Existing document methods
    # -------------------------------------------------------------------------

    def get_infocard(self, docid, revision=None):
        """Get the infocard (metadata) for a document by document number. revision defaults to 'released-revision' if not provided."""
        if revision is None:
            revision = 'released-revision'
        data_raw, headers = self.get(f"/document/{docid}/{revision}")
        data = json.loads(data_raw)
        return data

    def get_file_from_infocard(self, infocard, pdf=True):
        """Download the main file for a document given its infocard object. Returns (filename, base64-encoded content). Set pdf=False to get the native file instead of a PDF rendering."""
        infocardId = infocard['infocardId']
        endpoint = 'main-file-as-pdf' if pdf else 'mainFile'
        try:
            mainfile, headers = self.get(f"/document/{infocardId}/{endpoint}")
        except:
            return None, None
        
        content_disposition = headers.get('Content-Disposition')
        if content_disposition:
            match = re.match(r'attachment\s*;\s*filename="(.*)"\s*', content_disposition)
            if match:
                filename = match.group(1)
                return filename, base64.b64encode(mainfile).decode('utf-8')
        
        return None, base64.b64encode(mainfile).decode('utf-8')

    def get_file_and_infocard(self, docid, revision=None, pdf=True):
        """Get both the main file and the infocard metadata for a document in one call. Returns (filename, base64-encoded content, infocard dict)."""
        infocard = self.get_infocard(docid, revision)
        filename, mainfile = self.get_file_from_infocard(infocard, pdf)
        return filename, mainfile, infocard

    def get_file(self, docid, revision=None, pdf=True):
        """Download the main file for a document by document number and revision. Returns (filename, base64-encoded content)."""
        return self.get_file_and_infocard(docid, revision, pdf)[:2]

    def download_file(self, docid, revision=None, pdf=True):
        """Download and save a document's main file to the local data directory. Returns the path where the file was saved."""
        filename, mainfile, infocard = self.get_file_and_infocard(docid, revision, pdf)
        if filename and mainfile:
            file_path = os.path.join(self.data_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(mainfile))
            return f"File {filename} downloaded to {file_path}"
        return "File not found"

    # -------------------------------------------------------------------------
    # Phase 2: Document InfoCard extensions
    # -------------------------------------------------------------------------

    def get_infocard_by_id(self, infocardId):
        """Get a document infocard (metadata) by its numeric infocard ID."""
        data_raw, _ = self.get(f"/document/{infocardId}")
        return json.loads(data_raw)

    def get_infocard_details(self, infocardId):
        """Get extended details for a document infocard by its numeric infocard ID."""
        data_raw, _ = self.get(f"/document/{infocardId}/details")
        return json.loads(data_raw)

    def get_latest_revision(self, documentNumber):
        """Get the infocard for the latest revision of a document by document number."""
        data_raw, _ = self.get(f"/document/{documentNumber}/latest-revision")
        return json.loads(data_raw)

    def get_released_revision(self, documentNumber):
        """Get the infocard for the currently released revision of a document by document number."""
        data_raw, _ = self.get(f"/document/{documentNumber}/released-revision")
        return json.loads(data_raw)

    def get_next_revision(self, documentNumber, revision):
        """Get the infocard for the next revision after the specified revision of a document."""
        data_raw, _ = self.get(f"/document/{documentNumber}/{revision}/next-revision")
        return json.loads(data_raw)

    def get_previous_revision(self, documentNumber, revision):
        """Get the infocard for the previous revision before the specified revision of a document."""
        data_raw, _ = self.get(f"/document/{documentNumber}/{revision}/previous-revision")
        return json.loads(data_raw)

    def has_find_infocard_right(self, infocardId):
        """Check whether the current user has the right to find/view the specified infocard."""
        data_raw, _ = self.get(f"/hasFindInfoCardRight/{infocardId}")
        return json.loads(data_raw)

    def get_anonymous_vault_rights(self, infocardId):
        """Get the anonymous (public) vault access rights for the specified infocard."""
        data_raw, _ = self.get(f"/anonymous-vault-rights/{infocardId}")
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 3: Document file downloads
    # -------------------------------------------------------------------------

    def _download_binary(self, url):
        data_raw, headers = self.get(url)
        content_disposition = headers.get('Content-Disposition')
        filename = None
        if content_disposition:
            match = re.match(r'attachment\s*;\s*filename="(.*)"\s*', content_disposition)
            if match:
                filename = match.group(1)
        return filename, base64.b64encode(data_raw).decode('utf-8')

    def get_published_main_file(self, infoCardId):
        """Download the published main file for a document. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/document/{infoCardId}/publishedMainFile")

    def main_file_exists(self, infoCardId):
        """Check whether a main file exists for the specified document infocard."""
        data_raw, _ = self.get(f"/document/{infoCardId}/main-file-exists")
        return json.loads(data_raw)

    def encrypted_main_file_exists(self, infoCardId):
        """Check whether an encrypted main file exists for the specified document infocard."""
        data_raw, _ = self.get(f"/document/{infoCardId}/encryptedMainFileExists")
        return json.loads(data_raw)

    def published_main_file_exists(self, infoCardId):
        """Check whether a published main file exists for the specified document infocard."""
        data_raw, _ = self.get(f"/document/{infoCardId}/publishedMainFileExists")
        return json.loads(data_raw)

    def get_altered_published_pdf(self, infoCardId):
        """Download the altered fully-published PDF rendering of a document's main file. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/document/{infoCardId}/altered-fully-published-main-file")

    def get_modified_published_infocard(self, infoCardId):
        """Download the modified published infocard PDF for a document. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/document/{infoCardId}/modified-published-info-card")

    def get_published_infocard_pdf(self, infoCardId):
        """Download the published infocard PDF for a document. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/document/{infoCardId}/published-infocard")

    # -------------------------------------------------------------------------
    # Phase 4: Document attachments & links
    # -------------------------------------------------------------------------

    def get_attachments(self, infoCardId):
        """Get the list of attachments for a document infocard."""
        data_raw, _ = self.get(f"/document/{infoCardId}/attachments")
        return json.loads(data_raw)

    def get_attachment(self, infoCardId, attachmentId):
        """Download a specific attachment from a document infocard. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/document/{infoCardId}/attachments/{attachmentId}")

    def get_document_links(self, infoCardId):
        """Get all linked documents for a document infocard."""
        data_raw, _ = self.get(f"/document/{infoCardId}/links")
        return json.loads(data_raw)

    def get_document_links_metadata(self, infoCardId):
        """Get metadata about all linked documents for a document infocard."""
        data_raw, _ = self.get(f"/document/{infoCardId}/links-metadata")
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 5: Document types, settings & vault changes
    # -------------------------------------------------------------------------

    def get_document_types(self):
        """Get the list of all configured document types in the tenant."""
        data_raw, _ = self.get("/document/types")
        return json.loads(data_raw)

    def get_document_type_template(self, documentTypeId):
        """Download the template file for a document type. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/document/types/{documentTypeId}/template")

    def is_document_type(self, infoCardId):
        """Check whether the specified infocard is itself a document type definition."""
        data_raw, _ = self.get(f"/document/types/{infoCardId}/infocard-is-document-type")
        return json.loads(data_raw)

    def get_type_custom_fields(self, infocardTypeName):
        """Get the custom fields configured for a document type by type name."""
        data_raw, _ = self.get(f"/document/types/{infocardTypeName}/customfields")
        return json.loads(data_raw)

    def get_subtype_custom_fields(self, infocardTypeName, infocardSubTypeName):
        """Get the custom fields configured for a document subtype by type name and subtype name."""
        data_raw, _ = self.get(f"/document/types/{infocardTypeName}/subtypes/{infocardSubTypeName}/customfields")
        return json.loads(data_raw)

    def get_subtypes(self, parentId):
        """Get all subtypes defined under a parent document type ID."""
        data_raw, _ = self.get(f"/document/types/{parentId}/subtypes")
        return json.loads(data_raw)

    def get_document_settings(self):
        """Get global document settings for the tenant."""
        data_raw, _ = self.get("/document/settings")
        return json.loads(data_raw)

    def search_vault_changes(self, vaultId=None, startDate=None, endDate=None, page_number=None, page_size=None):
        """Search for documents whose vault has changed. Optionally filter by vaultId and date range (ISO 8601). Supports pagination via page_number and page_size."""
        url = self._build_url("/documents/search/infoCardVaultChange", {
            'vaultId': vaultId,
            'startDate': startDate,
            'endDate': endDate,
            'page-number': page_number,
            'page-size': page_size,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 6: Custom fields
    # -------------------------------------------------------------------------

    def get_custom_fields(self):
        """Get all custom fields configured in the tenant portal."""
        data_raw, _ = self.get("/portal/customfields")
        return json.loads(data_raw)

    def get_custom_data_field(self, customFieldName):
        """Get the options/values for a custom data field by its field name."""
        data_raw, _ = self.get(f"/portal/customfields/customdata/option/{customFieldName}")
        return json.loads(data_raw)

    def search_custom_fields_by_revision(self, documentNumber, revision, customFields=None):
        """Get custom field values for a document revision. Optionally filter to specific field names by passing a list to customFields."""
        url = f"/infocard/{documentNumber}/{revision}/customfield"
        if customFields:
            params = '&'.join(f"customFields={cf}" for cf in customFields)
            url = f"{url}?{params}"
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def search_custom_fields_by_infocard(self, infoCardId):
        """Get all custom field values for a document by its numeric infocard ID."""
        data_raw, _ = self.get(f"/infocard/{infoCardId}/customfield")
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 7: Data structures
    # -------------------------------------------------------------------------

    def get_data_structures(self):
        """Get a list of all data structures defined in the tenant portal."""
        data_raw, _ = self.get("/portal/datastructures")
        return json.loads(data_raw)

    def get_checklist_data_structures(self):
        """Get a list of all checklist-type data structures defined in the tenant portal."""
        data_raw, _ = self.get("/portal/checklist/datastructures")
        return json.loads(data_raw)

    def get_checklist_data_structure(self, id):
        """Get a specific checklist data structure by its ID."""
        data_raw, _ = self.get(f"/portal/checklist/datastructure/{id}")
        return json.loads(data_raw)

    def get_data_structure(self, id, attributes=None, filter=None):
        """Get all rows from a data structure by ID. Optionally filter columns with attributes (comma-separated field names) or filter rows with a filter expression."""
        url = self._build_url(f"/portal/datastructure/{id}", {
            'attributes': attributes,
            'filter': filter,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def get_data_structure_paginated(self, id, firstRow, pageSize, dataType=None, query=None):
        """Get a page of rows from a data structure. firstRow is the 0-based starting row index, pageSize is the number of rows to return. Optionally filter by dataType or a search query."""
        url = self._build_url(f"/portal/datastructure/paginated/{id}", {
            'firstRow': firstRow,
            'pageSize': pageSize,
            'dataType': dataType,
            'query': query,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def get_data_structure_filter_rows(self, id, attributes=None, filter=None):
        """Get filtered rows from a data structure by ID. Use attributes to limit returned columns and filter to narrow rows."""
        url = self._build_url(f"/portal/datastructure/{id}/filterRows", {
            'attributes': attributes,
            'filter': filter,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def get_data_structure_rights(self, id):
        """Get the access rights for a data structure by its ID."""
        data_raw, _ = self.get(f"/portal/datastructure-rights/{id}")
        return json.loads(data_raw)

    def get_data_structure_size(self, id, dataType=None, query=None):
        """Get the total number of records in a data structure. Optionally filter by dataType or a search query to count matching rows."""
        url = self._build_url(f"/portal/datastructure/{id}/record-size", {
            'dataType': dataType,
            'query': query,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def get_data_structure_row(self, id, rowId):
        """Get a single row from a data structure by data structure ID and row ID."""
        data_raw, _ = self.get(f"/portal/datastructure/{id}/row/{rowId}")
        return json.loads(data_raw)

    def get_next_number(self, id, lastNumber, dataStructureID):
        """Get the next auto-generated number for a data structure's numbering sequence given the last known number."""
        data_raw, _ = self.get(f"/portal/datastructure/numbering/{id}/{lastNumber}/{dataStructureID}")
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 8: Folders / Explorer
    # -------------------------------------------------------------------------

    def get_root_folders(self):
        """Get the top-level folder and document structure from the document explorer."""
        data_raw, _ = self.get("/explorer/folders/rootContent")
        return json.loads(data_raw)

    def get_taxonomy_folder(self, taxonomyID, path=""):
        """Get the contents of a taxonomy folder by taxonomy ID and optional sub-path."""
        url = f"/explorer/folders/taxonomy/{taxonomyID}/{path}".rstrip('/')
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def export_folder(self, folderId):
        """Export a folder and its contents as a downloadable archive. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/explorer/folders/{folderId}/export")

    def get_static_folder_content(self, folderId):
        """Get the contents of a static folder by its folder ID."""
        data_raw, _ = self.get(f"/explorer/folders/{folderId}/staticFolderContent")
        return json.loads(data_raw)

    def get_virtual_folder_content(self, parentFolderId, virtualFolderId):
        """Get the contents of a virtual folder by its parent folder ID and virtual folder ID."""
        data_raw, _ = self.get(f"/explorer/folders/{parentFolderId}/virtualFolderContent/{virtualFolderId}")
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 9: Forms
    # -------------------------------------------------------------------------

    def get_form_metadata(self, formNumber, revision):
        """Get the metadata/infocard for a form by form number and revision."""
        data_raw, _ = self.get(f"/forms/{formNumber}/{revision}")
        return json.loads(data_raw)

    def get_form_by_id(self, infocardId):
        """Get a form's metadata/infocard by its numeric infocard ID."""
        data_raw, _ = self.get(f"/forms/{infocardId}")
        return json.loads(data_raw)

    def get_form_attachments(self, infoCardId):
        """Get the list of attachments for a form infocard."""
        data_raw, _ = self.get(f"/forms/{infoCardId}/attachments")
        return json.loads(data_raw)

    def get_form_attachment(self, infoCardId, attachmentId):
        """Download a specific attachment from a form infocard. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/forms/{infoCardId}/attachments/{attachmentId}")

    def get_form_links(self, infoCardId):
        """Get all linked documents for a form infocard."""
        data_raw, _ = self.get(f"/forms/{infoCardId}/links")
        return json.loads(data_raw)

    def get_form_links_metadata(self, infoCardId):
        """Get metadata about all linked documents for a form infocard."""
        data_raw, _ = self.get(f"/forms/{infoCardId}/links-metadata")
        return json.loads(data_raw)

    def get_form_weblinks(self, infoCardId):
        """Get web links (URLs) attached to a form infocard."""
        data_raw, _ = self.get(f"/forms/{infoCardId}/weblinks")
        return json.loads(data_raw)

    def get_form_workflows(self):
        """Get all form workflow definitions configured in the tenant."""
        data_raw, _ = self.get("/forms/workflows")
        return json.loads(data_raw)

    def get_enabled_form_workflows(self):
        """Get only the currently enabled form workflow definitions in the tenant."""
        data_raw, _ = self.get("/forms/workflows/enabled")
        return json.loads(data_raw)

    def get_form_status(self, documentNumber):
        """Get the current workflow task/status for a form by its document number."""
        data_raw, _ = self.get(f"/forms/workflows/tasks/{documentNumber}")
        return json.loads(data_raw)

    def get_form_modified_published_pdf(self, infoCardId):
        """Download the modified published infocard PDF for a form. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/forms/{infoCardId}/modified-published-info-card")

    def get_form_published_pdf(self, infoCardId):
        """Download the published infocard PDF for a form. Returns (filename, base64-encoded content)."""
        return self._download_binary(f"/forms/{infoCardId}/published-infocard")

    # -------------------------------------------------------------------------
    # Phase 10: Portal admin — users, roles, vaults, business units
    # -------------------------------------------------------------------------

    def get_current_user(self):
        """Get the profile and details of the currently authenticated user."""
        data_raw, _ = self.get("/users/current-user")
        return json.loads(data_raw)

    def get_application_rights(self, applicationName=None, page_number=None, page_size=None):
        """Get portal application rights. Optionally filter by applicationName and paginate with page_number and page_size."""
        url = self._build_url("/portal/rights", {
            'applicationName': applicationName,
            'page-number': page_number,
            'page-size': page_size,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def get_business_units(self):
        """Get all business units configured in the tenant portal."""
        data_raw, _ = self.get("/portal/business-units")
        return json.loads(data_raw)

    def get_user_business_units(self, userId):
        """Get the business units assigned to a specific user by their user ID."""
        data_raw, _ = self.get(f"/portal/business-units/edit-user/{userId}")
        return json.loads(data_raw)

    def get_business_unit_roles(self, name, page_number=None, page_size=None):
        """Get roles associated with a business unit by its name. Supports pagination via page_number and page_size."""
        url = self._build_url(f"/portal/business-units/{name}/roles", {
            'page-number': page_number,
            'page-size': page_size,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def get_coversheets(self, page_number=None, page_size=None):
        """Get available publishing coversheets. Supports pagination via page_number and page_size."""
        url = self._build_url("/portal/publishing/coversheets", {
            'page-number': page_number,
            'page-size': page_size,
        })
        data_raw, _ = self.get(url)
        return json.loads(data_raw)

    def get_roles(self):
        """Get all roles defined in the tenant portal."""
        data_raw, _ = self.get("/portal/roles")
        return json.loads(data_raw)

    def get_user_username(self, userId):
        """Get username of user from ID."""
        data_raw, _ = self.get(f"/users/{userId}/interactable-roles")
        user_interactable_roles = json.loads(data_raw)
        return user_interactable_roles["username"]

    def get_role_members(self, name):
        """Get all users assigned to a specific role by role name."""
        data_raw, _ = self.get(f"/portal/roles/{name}/users")
        return json.loads(data_raw)

    def get_user_interactable_roles(self, userId):
        """Get the roles a specific user can interact with (e.g. delegate tasks to) by user ID."""
        data_raw, _ = self.get(f"/users/{userId}/interactable-roles")
        return json.loads(data_raw)

    def get_user_roles(self, userId):
        """Get all roles assigned to a specific user by user ID."""
        data_raw, _ = self.get(f"/users/{userId}/roles")
        return json.loads(data_raw)

    def get_vaults(self):
        """Get all vaults configured in the tenant portal."""
        data_raw, _ = self.get("/portal/vaults")
        return json.loads(data_raw)

    def get_vault_publishing_settings(self, vault):
        """Get the publishing settings for a specific vault by vault name."""
        data_raw, _ = self.get(f"/portal/vaults/{vault}/publishing/settings")
        return json.loads(data_raw)

    def get_lifecycles(self):
        """Get all document lifecycle definitions configured in the tenant portal."""
        data_raw, _ = self.get("/portal/lifecycles")
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 11: Suppliers, supplied items & registrations
    # -------------------------------------------------------------------------

    def get_supplied_items(self):
        """Get all supplied items tracked in the tenant."""
        data_raw, _ = self.get("/suppliedItems")
        return json.loads(data_raw)

    def get_item_suppliers(self, infoCardId):
        """Get all suppliers associated with a specific supplied item by its infocard ID."""
        data_raw, _ = self.get(f"/suppliedItems/{infoCardId}/suppliers")
        return json.loads(data_raw)

    def get_suppliers(self):
        """Get all suppliers configured in the tenant."""
        data_raw, _ = self.get("/suppliers")
        return json.loads(data_raw)

    def get_supplier(self, supplierId):
        """Get details for a specific supplier by their supplier ID."""
        data_raw, _ = self.get(f"/suppliers/{supplierId}")
        return json.loads(data_raw)

    def get_supplier_items(self, supplierId):
        """Get all supplied items provided by a specific supplier by their supplier ID."""
        data_raw, _ = self.get(f"/suppliers/{supplierId}/suppliedItems")
        return json.loads(data_raw)

    def get_registrations(self):
        """Get all supplier/product registrations in the tenant."""
        data_raw, _ = self.get("/registrations")
        return json.loads(data_raw)

    def get_registration(self, id):
        """Get a specific supplier/product registration by its ID."""
        data_raw, _ = self.get(f"/registrations/{id}")
        return json.loads(data_raw)

    # -------------------------------------------------------------------------
    # Phase 12: SCIM users & open-source licenses
    # -------------------------------------------------------------------------

    def get_scim_users(self, filter=None, startIndex=None, count=None):
        """List users via the SCIM v0 API. Optionally filter with a SCIM filter expression, and paginate with startIndex and count."""
        url = self._build_url("/Users", {
            'filter': filter,
            'startIndex': startIndex,
            'count': count,
        })
        data_raw, _ = self.get(url, base_path="/scim/v0")
        return json.loads(data_raw)

    def get_scim_user(self, resourceUserId):
        """Get a specific user's SCIM record by their SCIM resource user ID."""
        data_raw, _ = self.get(f"/Users/{resourceUserId}", base_path="/scim/v0")
        return json.loads(data_raw)

    def get_third_party_licenses(self):
        """Get the list of third-party open-source licenses used by MasterControl."""
        data_raw, _ = self.get("/portal/third-party-licenses")
        return json.loads(data_raw)

    def get_angular_license(self):
        """Get the Angular framework open-source license text used by MasterControl."""
        data_raw, _ = self.get("/portal/third-party-licenses/angular")
        return json.loads(data_raw)
