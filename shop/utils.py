
from django.utils.text import slugify


def generate_unique_slug(model, value, max_length=30):
    """Insure uniqueness of slugs

    If an object with the same slug already exists,
    add a number to this new slug. (like duplicate-slug-2)
    """

    base_slug = slugify(value[:max_length])
    slug = base_slug
    counter = 2

    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def product_image_upload_path(instance, filename):
    """Return the file path for product images."""

    return f"products/{instance.product.id}/{filename}"
