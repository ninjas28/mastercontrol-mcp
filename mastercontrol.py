import base64
import http.client
import json
import re
import os

class MasterControl:
    def __init__(self, key, tenant, data_dir):
        self.key = key
        self.tenant = tenant
        self.data_dir = data_dir
        self.conn = http.client.HTTPSConnection(f"{tenant}.mastercontrol.com")

    def get(self, url):
        self.conn.request("GET", f"/{self.tenant}/restapi/v1{url}", headers={'Authorization': f'Bearer {self.key}'})
        res = self.conn.getresponse()
        data = res.read()
        assert res.status == 200
        return data, dict(res.getheaders())

    def get_infocard(self, docid, revision=None):
        if revision is None:
            revision = 'released-revision'
        data_raw, headers = self.get(f"/document/{docid}/{revision}")
        data = json.loads(data_raw)
        return data

    def get_file_from_infocard(self, infocard, pdf=True):
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
        infocard = self.get_infocard(docid, revision)
        filename, mainfile = self.get_file_from_infocard(infocard, pdf)
        return filename, mainfile, infocard

    def get_file(self, docid, revision=None, pdf=True):
        return self.get_file_and_infocard(docid, revision, pdf)[:2]

    def download_file(self, docid, revision=None, pdf=True):
        filename, mainfile, infocard = self.get_file_and_infocard(docid, revision, pdf)
        if filename and mainfile:
            file_path = os.path.join(self.data_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(mainfile))
            return f"File {filename} downloaded to {file_path}"
        return "File not found"
