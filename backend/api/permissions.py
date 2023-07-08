from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Автор объекта или администратор - только им доступно
    изменение и удаление объекта.
    Другим пользователям доступно только чтение.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author.username == request.user.username
                or request.user.is_admin)


class IsNewUserAuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Автор объекта или администратор - только им доступно
    изменение и удаление объекта.
    Новый пользователь может создавать учетную запись.
    Другим пользователям доступно только чтение.
    """
    def has_permission(self, request, view):
        if (
            request.method in permissions.SAFE_METHODS
            or request.method == 'POST'
        ):
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author.username == request.user.username
                or request.user.is_admin)


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Автор объекта или администратор - только ему доступно
    изменение и удаление рецепта.
    Другим пользователям доступ закрыт.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (obj.author.username == request.user.username
                or request.user.is_admin)
