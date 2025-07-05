import unittest
from unittest.mock import patch, MagicMock
from mastercontrol import MasterControl
import json
import os
import base64

class TestMasterControl(unittest.TestCase):

    def setUp(self):
        self.data_dir = 'test_data'
        os.makedirs(self.data_dir, exist_ok=True)

    def tearDown(self):
        for f in os.listdir(self.data_dir):
            os.remove(os.path.join(self.data_dir, f))
        os.rmdir(self.data_dir)

    @patch('mastercontrol.http.client.HTTPSConnection')
    def test_get_infocard(self, mock_connection):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({'infocardId': '123', 'title': 'Test Document'}).encode()
        mock_response.getheaders.return_value = {}
        mock_connection.return_value.getresponse.return_value = mock_response

        mc = MasterControl('test_key', 'test_tenant', self.data_dir)
        infocard = mc.get_infocard('DOC-123')

        self.assertEqual(infocard['infocardId'], '123')
        self.assertEqual(infocard['title'], 'Test Document')

    @patch('mastercontrol.http.client.HTTPSConnection')
    def test_get_file_from_infocard(self, mock_connection):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'file_content'
        mock_response.getheaders.return_value = {'Content-Disposition': 'attachment; filename="test.pdf"'}
        mock_connection.return_value.getresponse.return_value = mock_response

        mc = MasterControl('test_key', 'test_tenant', self.data_dir)
        filename, mainfile = mc.get_file_from_infocard({'infocardId': '123'})

        self.assertEqual(filename, 'test.pdf')
        self.assertEqual(base64.b64decode(mainfile), b'file_content')

    @patch('mastercontrol.http.client.HTTPSConnection')
    def test_download_file(self, mock_connection):
        mock_infocard_response = MagicMock()
        mock_infocard_response.status = 200
        mock_infocard_response.read.return_value = json.dumps({'infocardId': '123', 'title': 'Test Document'}).encode()
        mock_infocard_response.getheaders.return_value = {}

        mock_file_response = MagicMock()
        mock_file_response.status = 200
        mock_file_response.read.return_value = b'file_content'
        mock_file_response.getheaders.return_value = {'Content-Disposition': 'attachment; filename="test.pdf"'}

        mock_connection.return_value.getresponse.side_effect = [mock_infocard_response, mock_file_response]

        mc = MasterControl('test_key', 'test_tenant', self.data_dir)
        result = mc.download_file('DOC-123')

        file_path = os.path.join(self.data_dir, 'test.pdf')
        self.assertEqual(result, f"File test.pdf downloaded to {file_path}")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'rb') as f:
            self.assertEqual(f.read(), b'file_content')

if __name__ == '__main__':
    unittest.main()
