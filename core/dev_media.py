"""Development only: serve MEDIA_ROOT with HTTP range requests.

Django's static `serve` view ignores the Range header, but the map tiles
(PMTiles, ADR 0015) are read in byte ranges. In production Caddy serves
/media/ and supports ranges itself. Mounted in config/urls.py only when
DEBUG is on.
"""

import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404, HttpResponse
from django.utils._os import safe_join

RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")


def serve_media(request, path):
    try:
        full_path = Path(safe_join(settings.MEDIA_ROOT, path))
    except SuspiciousFileOperation as error:
        raise Http404 from error
    if not full_path.is_file():
        raise Http404

    size = full_path.stat().st_size
    content_type = mimetypes.guess_type(full_path.name)[0] or "application/octet-stream"
    match = RANGE.match(request.headers.get("Range", ""))
    if not match or match.groups() == ("", ""):
        response = FileResponse(full_path.open("rb"), content_type=content_type)
        response["Accept-Ranges"] = "bytes"
        return response

    first, last = match.groups()
    if first:
        start, end = int(first), int(last) if last else size - 1
    else:  # suffix range: the last N bytes
        start, end = max(size - int(last), 0), size - 1
    end = min(end, size - 1)
    if start > end:
        response = HttpResponse(status=416)
        response["Content-Range"] = f"bytes */{size}"
        return response

    with full_path.open("rb") as file:
        file.seek(start)
        data = file.read(end - start + 1)
    response = HttpResponse(data, status=206, content_type=content_type)
    response["Content-Range"] = f"bytes {start}-{end}/{size}"
    response["Accept-Ranges"] = "bytes"
    return response
