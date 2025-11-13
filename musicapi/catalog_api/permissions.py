from rest_framework import permissions

class IsAuthenticatedReadOnly(permissions.BasePermission):
    """
    Permission qui permet :
    - GET/HEAD/OPTIONS pour tous les utilisateurs AUTHENTIFIÉS
    - Refuse POST/PUT/PATCH/DELETE
    """
    
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False

class IsContributorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_staff:
            return True
        
        if request.user.groups.filter(name='Contributeur_BGK').exists():
            return True
        return False
    