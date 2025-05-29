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
    """
    Custom permission class for EvibesViewSet endpoints.

    - 'create' may be explicitly allowed via view.additional['create'] == 'ALLOW'.
    - Certain actions are scoped to the request.user’s own objects.
    - Standard model perms ('add', 'view', 'change', 'delete') are enforced for all other actions,
      including for staff users.
    - Publicly visible models allow anonymous list/retrieve.
    - If an instance or queryset has a "user" attribute, ensure that the request.user is the same,
      unless the user is an admin with the required django permission.
    """

    ACTION_PERM_MAP = {
        "retrieve": "view",
        "list": "view",
        "create": "add",
        "update": "change",
        "partial_update": "change",
        "destroy": "delete",
    }

    USER_SCOPED_ACTIONS = {
        "buy",
        "buy_unregistered",
        "current",
        "add_order_product",
        "remove_order_product",
        "add_wishlist_product",
        "remove_wishlist_product",
        "bulk_add_wishlist_products",
        "bulk_remove_wishlist_products",
        "autocomplete",
    }

    def has_permission(self, request, view):
        action = getattr(view, "action", None)
        model = view.queryset.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        if action == "create" and view.additional.get("create") == "ALLOW":
            return True

        if action in self.USER_SCOPED_ACTIONS:
            return True

        perm_prefix = self.ACTION_PERM_MAP.get(action)
        if perm_prefix:
            codename = f"{perm_prefix}_{model_name}"
            if request.user.has_perm(f"{app_label}.{codename}"):
                return True

        return bool(
            action in ("list", "retrieve")
            and getattr(model, "is_publicly_visible", False)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, "user"):
            if obj.user == request.user:
                return True
            # Allow admins who hold the required model permission
            app_label = obj._meta.app_label
            model_name = obj._meta.model_name
            action = getattr(view, "action", None)
            perm_prefix = self.ACTION_PERM_MAP.get(action)
            return bool(perm_prefix and request.user.has_perm(f"{app_label}.{perm_prefix}_{model_name}"))

        model = view.queryset.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        action = getattr(view, "action", None)
        perm_prefix = self.ACTION_PERM_MAP.get(action)
        return bool(perm_prefix and request.user.has_perm(f"{app_label}.{perm_prefix}_{model_name}"))

    def has_queryset_permission(self, request, view, queryset):
        """
        Filter the base queryset according to the action and user.
        For models with a "user" field, restrict access to records belonging to the request user
        unless the admin holds the needed permissions.
        """
        model = view.queryset.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        if hasattr(model, "user"):
            if view.action in self.USER_SCOPED_ACTIONS:
                return queryset.filter(user=request.user)
            if view.action in ("list", "retrieve"):
                if request.user.has_perm(f"{app_label}.view_{model_name}"):
                    if request.user.is_staff:
                        return queryset
                    return queryset.filter(user=request.user, is_active=True)
                return queryset.none()

            base = queryset.filter(is_active=True, user=request.user)
            if request.user.is_staff and request.user.has_perm(
                    f"{app_label}.{self.ACTION_PERM_MAP.get(view.action)}_{model_name}"
            ):
                return queryset.filter(is_active=True)
            return base

        if view.action in ("list", "retrieve"):
            if request.user.has_perm(f"{app_label}.view_{model_name}"):
                if request.user.is_staff:
                    return queryset
                return queryset.filter(is_active=True)
            return queryset.none()

        base = queryset.filter(is_active=True)
        match view.action:
            case "update" | "partial_update":
                if request.user.has_perm(f"{app_label}.change_{model_name}"):
                    return base
            case "destroy":
                if request.user.has_perm(f"{app_label}.delete_{model_name}"):
                    return base

        return queryset.none()
