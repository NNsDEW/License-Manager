from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Админы могут всё, остальные только читать.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_staff)


class IsAdminOrReadCreateOrOwner(BasePermission):
    """
    GET, POST — всем авторизованным.
    PUT, PATCH, DELETE — только админ или владелец объекта (owner == request.user).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS or request.method == "POST":
            return True
        return bool(request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None)
        return owner is not None and owner == request.user

