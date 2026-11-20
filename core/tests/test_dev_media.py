import tempfile
from pathlib import Path

from django.test import RequestFactory, SimpleTestCase, override_settings

from core.dev_media import serve_media


class DevMediaRangeTests(SimpleTestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        Path(self.dir.name, "maps").mkdir()
        Path(self.dir.name, "maps", "t.pmtiles").write_bytes(bytes(range(100)))
        self.settings = override_settings(MEDIA_ROOT=self.dir.name)
        self.settings.enable()

    def tearDown(self):
        self.settings.disable()
        self.dir.cleanup()

    def get(self, **headers):
        request = RequestFactory().get("/media/maps/t.pmtiles", headers=headers)
        return serve_media(request, "maps/t.pmtiles")

    def test_whole_file(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Accept-Ranges"], "bytes")
        self.assertEqual(b"".join(response.streaming_content), bytes(range(100)))

    def test_byte_range(self):
        response = self.get(Range="bytes=10-19")
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response.content, bytes(range(10, 20)))
        self.assertEqual(response["Content-Range"], "bytes 10-19/100")

    def test_open_and_suffix_ranges(self):
        self.assertEqual(self.get(Range="bytes=95-").content, bytes(range(95, 100)))
        self.assertEqual(self.get(Range="bytes=-3").content, bytes(range(97, 100)))

    def test_unsatisfiable_range(self):
        self.assertEqual(self.get(Range="bytes=200-300").status_code, 416)

    def test_path_traversal_is_rejected(self):
        from django.http import Http404

        request = RequestFactory().get("/media/../settings.py")
        with self.assertRaises(Http404):
            serve_media(request, "../settings.py")
