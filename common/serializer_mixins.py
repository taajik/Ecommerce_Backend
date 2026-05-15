
from rest_framework.exceptions import MethodNotAllowed


class ReadOnlyMixin:
    """Mark all serializer fields read-only
    and disallow creation and update.
    """

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

    def create(self, validated_data):
        raise MethodNotAllowed("POST", detail="Creation not allowed.")

    def update(self, instance, validated_data):
        raise MethodNotAllowed("PUT", detail="Update not allowed.")
