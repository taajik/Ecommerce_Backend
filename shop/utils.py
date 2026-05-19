
import os
import uuid


def product_image_upload_path(instance, filename):
    """Return the file path for product images."""

    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return f"products/{instance.product.id}/{new_filename}"
