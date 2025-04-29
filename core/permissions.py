from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class EvibesPermission(permissions.BasePermission):
    def _get_permission_codename(self, action, view):
        action_permission_map = {
            "retrieve": "view",
            "list": "view",
            "create": "add",
            "update": "change",
            "partial_update": "change",
            "destroy": "delete",
        }
        model_name = view.queryset.model._meta.model_name  # Get the model name
        permission_type = action_permission_map.get(action)

        if permission_type:
            return f"core.{permission_type}_{model_name}"
        return None

    def has_queryset_permission(self, request, view, queryset):
        if request.user.is_staff:
            return queryset
        if view.action in [
            "buy",
            "current",
            "add_order_product",
            "remove_order_product",
            "add_wishlist_product",
            "remove_wishlist_product",
            "bulk_add_wishlist_products",
            "bulk_remove_wishlist_products",
        ]:
            return queryset.filter(user=request.user)
        return queryset.filter(is_active=True)

    def has_permission(self, request, view):
        action = getattr(view, "action", None)

        if action in [
            "buy",
            "current",
            "add_order_product",
            "remove_order_product",
            "add_wishlist_product",
            "remove_wishlist_product",
            "bulk_add_wishlist_products",
            "bulk_remove_wishlist_products",
        ]:
            return True

        required_permission = self._get_permission_codename(action, view)

        if required_permission and request.user.has_perm(required_permission):
            return True

        return view.queryset.model.is_publicly_visible and action in ["retrieve", "list"]
