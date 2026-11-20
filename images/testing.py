"""Test helpers for images."""

from django.core.files.images import ImageFile
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file


def make_image(**kwargs):
    test_file = get_test_image_file()
    defaults = {
        "title": "Test image",
        "file": ImageFile(test_file.file, name="test.png"),
        "description": "A test image",
        "credit": "Photo: [Name]",
        "licence": "CC BY-SA 4.0",
    }
    return get_image_model().objects.create(**(defaults | kwargs))
