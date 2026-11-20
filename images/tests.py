from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wagtail.images import get_image_model
from wagtail.images.forms import get_image_form
from wagtail.images.tests.utils import get_test_image_file


class CustomImageFormTests(TestCase):
    def form(self, **data):
        form_class = get_image_form(get_image_model())
        image = get_test_image_file()
        files = {"file": SimpleUploadedFile(image.name, image.file.getvalue())}
        return form_class(data={"title": "Ararat", **data}, files=files)

    def test_is_the_wagtail_image_model(self):
        self.assertEqual(get_image_model()._meta.label, "images.CustomImage")

    def test_alt_text_credit_and_licence_are_required(self):
        form = self.form()
        self.assertFalse(form.is_valid())
        for field in ("description", "credit", "licence"):
            self.assertIn(field, form.errors)

    def test_valid_with_alt_text_credit_and_licence(self):
        form = self.form(
            description="Mount Ararat at dusk",
            credit="Photo: [Name]",
            licence="CC BY-SA 4.0",
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_alt_text_is_the_default_alt_text(self):
        image = get_image_model()(title="Ararat", description="Mount Ararat")
        self.assertEqual(image.default_alt_text, "Mount Ararat")
