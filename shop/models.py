
import os

from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.utils import timezone
from PIL import Image as PILImage

from .utils import generate_unique_slug, product_image_upload_path


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(BaseModel):
    """Core entity that represents a sellable product in the shop."""

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    stock = models.PositiveIntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    slug = models.SlugField(
        max_length=255,
        allow_unicode=True,
        unique=True,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.title,
                                             max_length=255)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Product {self.title}"


class ProductImage(BaseModel):
    """Stores data of an image associated with a product.

    The order to display the images is specified using the 'position' field.
    A thumbnail is generated only for the first image of a product.
    """

    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to=product_image_upload_path)
    thumbnail = models.ImageField(blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveSmallIntegerField(default=0, blank=True)

    class Meta:
        ordering = ["position"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.position == 0:
            self.generate_thumbnail()

    def __str__(self):
        return f"Image ({self.position}) for product {self.product_id}"

    def generate_thumbnail(self):
        """Generate and save the thumbnail version of this image."""
        if not self.image:
            return
        if self.thumbnail and os.path.isfile(self.thumbnail.path):
            return

        img = PILImage.open(self.image.path)
        img.thumbnail((200, 200))

        dir_name = os.path.basename(os.path.dirname(self.image.path))
        thumb_name = f"thumb_{dir_name}_{os.path.basename(self.image.name)}"
        thumb_path = os.path.join("products/thumbnails", thumb_name)
        full_path = os.path.join(settings.MEDIA_ROOT, thumb_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        img.save(full_path)

        self.thumbnail.name = thumb_path
        super().save(update_fields=["thumbnail"])


class Comment(BaseModel):
    """User-generated comment or review on a product."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    reply_to = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )
    text = models.TextField(validators=[MaxLengthValidator(1500)])
    is_approved = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"Comment {self.pk} by user {self.user_id} on product {self.product_id}"


class Category(models.Model):
    """Grouping for products.

    Products can belong to multiple categories.
    """

    products = models.ManyToManyField(
        Product,
        related_name="categories",
        blank=True,
    )
    title = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(
        max_length=30,
        allow_unicode=True,
        unique=True,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Category {self.title}"


class CartItem(models.Model):
    """Intermediate model for relations between carts and products.

    Stores the quantity so only on instance of
    a product is stored in the cart.
    """

    cart = models.ForeignKey(
        "Cart",
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="cart_items",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("cart", "product"),
                name="item_in_cart_once_constraint"
            )
        ]

    def __str__(self):
        return f"Cart Item (product {self.product_id})"


class Cart(models.Model):
    """Shopping cart associated with a single user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    products = models.ManyToManyField(
        Product,
        through=CartItem,
        blank=True,
        related_name="carts",
    )

    def __str__(self):
        return f"Cart of user {self.user_id}"


class OrderItem(models.Model):
    """Intermediate model for relations between orders and products.

    Stores price at purchase time and quantity to ensure historical
    accuracy even if product data changes later.
    """

    order = models.ForeignKey(
        "Order",
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        null=True,
        related_name="order_items",
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(
        default=1,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("order", "product"),
                name="item_in_order_once_constraint"
            )
        ]

    def __str__(self):
        return f"Order item (product {self.product_id})"


class Order(BaseModel):
    """Represents a finalized purchase made by a user."""

    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    STATUS_CHOICES = {
        PENDING: "Pending",
        PAID: "Paid",
        SHIPPED: "Shipped",
        DELIVERED: "Delivered",
        CANCELLED: "Cancelled",
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE,
    )
    products = models.ManyToManyField(
        Product,
        through=OrderItem,
        blank=True,
        related_name="orders",
    )
    total_price = models.DecimalField(  # TODO: should be calculated automatically
        max_digits=12,
        decimal_places=2,
        default=0,
        blank=True,
    )
    shipping_address = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        creation_time = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"Order by user {self.user_id} at {creation_time}"


class Payment(BaseModel):
    """Payment record for an order."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REFUNDED = "REFUNDED"
    STATUS_CHOICES = {
        PENDING: "Pending",
        PROCESSING: "Processing",
        PAID: "Paid",
        FAILED: "Failed",
        CANCELLED: "Cancelled",
        EXPIRED: "Expired",
        REFUNDED: "Refunded",
    }

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    provider = models.CharField(max_length=30)
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return f"Payment {self.transaction_id}"


class Address(BaseModel):
    """Addresses a user defines in their profile."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="addresses",
        on_delete=models.CASCADE,
    )
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30)
    address_line = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=30)

    def get_full_address(self):
        address_list = [self.country, self.state, self.city, self.address_line]
        return ", ".join(filter(None, address_list))

    def __str__(self):
        return f"Address of user {self.user_id}"
