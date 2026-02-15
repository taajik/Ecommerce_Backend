
from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models

from .utils import generate_unique_slug


class Product(models.Model):
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
            self.slug = generate_unique_slug(Product, self.title)
        super().save(*args, **kwargs)


class Comment(models.Model):
    """User-generated comment or review on a product."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )
    text = models.TextField(validators=[MaxLengthValidator(1500)])


class Category(models.Model):
    """Grouping for products.

    Products can belong to multiple categories.
    """

    products = models.ManyToManyField(Product, blank=True)
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


class CartItem(models.Model):
    """Intermediate model for relations between carts and products.

    Stores the quantity so only on instance of
    a product is stored in the cart.
    """

    cart = models.ForeignKey(
        "Cart",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
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
    )


class OrderItem(models.Model):
    """Intermediate model for relations between orders and products.

    Stores price at purchase time and quantity to ensure historical
    accuracy even if product data changes later.
    """

    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        null=True,
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


class Order(models.Model):
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
        on_delete=models.CASCADE,
    )
    products = models.ManyToManyField(
        Product,
        through=OrderItem,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    total_price = models.DecimalField(  # TODO: should be calculated automatically
        max_digits=12,
        decimal_places=2,
        default=0,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    """Payment record for an order."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    provider = models.CharField(max_length=30)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Address(models.Model):
    """Addresses a user defines in their profile."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30)
    address_line = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=30)
