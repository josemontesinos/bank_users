from rest_framework.permissions import BasePermission


MANIPULATION_METHODS = ('PUT', 'PATCH', 'DELETE')

PERMS_MAP = {
    'PUT': 'users.change_user',
    'PATCH': 'users.change_user',
    'DELETE': 'users.delete_user',
}


class CanManipulateUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method not in MANIPULATION_METHODS or \
               request.user.has_perm(PERMS_MAP[request.method], obj)
