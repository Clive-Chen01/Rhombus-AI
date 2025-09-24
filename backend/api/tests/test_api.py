from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile


CSV = """ID,Name,Email\n1,John,john@example.com\n2,Jane,jane@site.org\n""".encode()


class APISmoke(TestCase):
    def setUp(self):
        self.client = Client()


def test_upload_and_transform(self):
    up = SimpleUploadedFile("sample.csv", CSV, content_type="text/csv")
    r = self.client.post("/api/upload", {"file": up})
    self.assertEqual(r.status_code, 200)


    body = {
        "natural_language": "Find email addresses",
        "replacement": "REDACTED"
    }
    r2 = self.client.post("/api/transform", body, content_type="application/json")
    self.assertEqual(r2.status_code, 200)
    self.assertIn("REDACTED", str(r2.json()))