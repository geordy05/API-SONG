from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle  # <-- 1. AJOUTER CET IMPORT
import logging

logger = logging.getLogger(__name__) 
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
    """
    Permet la lecture (GET) à tous les authentifiés.
    Permet l'écriture (POST, PUT, DELETE) uniquement aux Contributeurs ou Admins.
    """
    def has_permission(self, request, view):
        # Cas 1: Lecture (GET, HEAD, OPTIONS)
        # On autorise tous les utilisateurs authentifiés (comme demandé dans la Partie 1)
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Cas 2: Écriture (POST, PUT, DELETE)
        # On vérifie si l'utilisateur est admin OU membre du groupe "Contributeurs"
        is_admin = request.user and request.user.is_staff
        is_contributor = request.user and request.user.groups.filter(name='Contributeurs').exists()
        
        if is_admin or is_contributor:
            return True

        # ----------------------------------------------
        # 3. AJOUTER LE LOGGING ICI
        # ----------------------------------------------
        # Si on arrive ici, c'est que l'utilisateur n'est NI admin, NI contributeur
        # ET qu'il tente une action d'ÉCRITURE. C'est un refus de permission.
        
        logger.warning(
            f"Tentative d'accès non autorisée (Écriture) par l'utilisateur: {request.user.username} "
            f"sur la vue: {view.basename}"
        )
        return False
class CreateArtistThrottle(UserRateThrottle):
    """
    Limite la création d'artistes à 10 par heure pour un utilisateur donné.
    """
    # Note : 'rate' ne fonctionne que si 'scope' n'est pas défini.
    # C'est exactement ce que demande le TP.
    rate = '10/hour'