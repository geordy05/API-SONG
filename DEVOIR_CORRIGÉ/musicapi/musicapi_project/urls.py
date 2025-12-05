"""
URL configuration for musicapi_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.http import HttpResponseForbidden # <--- AJOUT 1
from .schema import schema # <--- AJOUT 2
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# --- AJOUT 3 : Vue personnalisée pour forcer le 403 ---
class PrivateGraphQLView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        # Si l'utilisateur n'est pas connecté, on coupe tout de suite avec une 403
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Non autorisé")
        return super().dispatch(request, *args, **kwargs)
# ------------------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/catalog/', include('catalog_api.urls')),
    
    # --- MODIFICATION ICI : On utilise PrivateGraphQLView ---
    path('graphql/', csrf_exempt(PrivateGraphQLView.as_view(graphiql=True, schema=schema))),
    # --------------------------------------------------------

    path('', include('web_interface.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # URL pour le schéma OpenAPI (fichier .yaml)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # URL pour Swagger UI (l'interface interactive)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # URL pour ReDoc (une autre interface de doc)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]