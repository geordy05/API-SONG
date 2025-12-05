# Dans playlist_api/utils.py

from graphql import GraphQLError
from .models import User as AppUser 
from .models import User as AppUser
from graphql import GraphQLError

def get_or_create_app_user_from_info(info):
    user = info.context.user
    
    if not user.is_authenticated:
        raise GraphQLError("Utilisateur non connecté.")

    # On utilise le USERNAME comme clé de liaison (car l'email peut être vide ou changer)
    try:
        app_user, created = AppUser.objects.get_or_create(
            username=user.username,
            defaults={
                'email': user.email if user.email else f"{user.username}@placeholder.com"
            }
        )
        
        # Optionnel : Si l'utilisateur existe déjà mais a changé d'email dans Django Admin
        if not created and user.email and app_user.email != user.email:
            app_user.email = user.email
            app_user.save()
            
        return app_user

    except Exception as e:
        # C'est ici que tu attrapais l'erreur 'duplicate key'
        raise GraphQLError(f"Erreur lors de la récupération/création de l'utilisateur de l'application: {str(e)}")