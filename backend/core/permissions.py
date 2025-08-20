from rest_framework.permissions import BasePermission, SAFE_METHODS

ROLE_WEIGHT = {'viewer':0, 'editor':1, 'admin':2}

class HasRole(BasePermission):
    required_role = 'viewer'
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None) or request.headers.get('X-Role') or 'viewer'
        weight = ROLE_WEIGHT.get(role, 0)
        need = ROLE_WEIGHT.get(getattr(view, 'required_role','viewer'), 0)
        return weight >= need

class IsEditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        role = request.headers.get('X-Role', 'viewer')
        return ROLE_WEIGHT.get(role,0) >= ROLE_WEIGHT['editor']

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        role = request.headers.get('X-Role', 'viewer')
        return ROLE_WEIGHT.get(role,0) >= ROLE_WEIGHT['admin']
