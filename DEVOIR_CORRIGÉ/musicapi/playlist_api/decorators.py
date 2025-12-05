import functools
from graphql import GraphQLError
from oauth2_provider.models import AccessToken

def oauth2_required(fn):
    """
    Décorateur pour vérifier l'authentification OAuth2 
    et attacher l'utilisateur au contexte.
    """
    @functools.wraps(fn)
    def wrapper(self, info, **kwargs):
        # Récupérer le contexte (la requête HTTP)
        request = info.context
        
        # 1. Extraire le token du header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            raise GraphQLError("Authentication required. Header 'Authorization: Bearer <token>' manquant.")

        token_str = auth_header.split(' ')[1]

        try:
            # 2. Vérifier que le token existe dans la base de données
            token = AccessToken.objects.get(token=token_str)
            
            # 3. Vérifier que le token n'est pas expiré
            if token.is_expired():
                raise GraphQLError("Token expired")

            # 4. Attacher l'utilisateur Django au contexte
            # C'est l'étape clé !
            info.context.user = token.user

        except AccessToken.DoesNotExist:
            raise GraphQLError("Invalid token")
        
        # Si tout est OK, exécuter la mutation/query originale
        return fn(self, info, **kwargs)

    return wrapper