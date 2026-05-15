
def product_image_upload_path(instance, filename):
    """Return the file path for product images."""

    return f"products/{instance.product.id}/{filename}"
