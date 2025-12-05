import pytest
from rest_framework.test import APIClient
from playlist_api.models import Playlist, User  # Import du modèle local
from oauth2_provider.models import Application
from django.contrib.auth.models import User as DjangoUser
from oauth2_provider.models import AccessToken
from django.utils import timezone
from datetime import timedelta
from django.test import Client

# --- Nettoyeur automatique ---
@pytest.fixture(autouse=True)
def clean_db(db):
    """
    S'exécute automatiquement avant chaque test.
    Vide la table Playlist pour garantir qu'on part de zéro.
    """
    Playlist.objects.all().delete()
# -----------------------------

@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()

@pytest.fixture
def sample_user(db):
    """Crée un utilisateur de test dans la table app_user"""
    user, created = User.objects.get_or_create(
        username='test_playlist_user', 
        defaults={'email': 'test@example.com'}
    )
    return user

@pytest.fixture
def sample_playlist(db, sample_user):
    """Crée une playlist de test"""
    # CORRECTION ICI : On met is_public=True pour qu'elle soit visible
    return Playlist.objects.create(
        name="My Awesome Playlist", 
        user=sample_user, 
        is_public=True 
    )

@pytest.fixture
def oauth_application():
    """Crée une application OAuth2 pour les tests."""
    return Application.objects.create(
        name='Test Application',
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_PASSWORD,
    )

@pytest.fixture
def authenticated_user():
    """Crée un utilisateur authentifié Django pour GraphQL."""
    return DjangoUser.objects.create_user(
        username='authenticated_user',
        email='authenticated@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(authenticated_user, oauth_application):
    """Client GraphQL authentifié avec token OAuth2."""
    access_token = AccessToken.objects.create(
        user=authenticated_user,
        token='test_oauth_token_authenticated',
        application=oauth_application,
        expires=timezone.now() + timedelta(hours=1),
        scope='read write'
    )
    client = Client()
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token.token}'
    return client

@pytest.fixture
def unauthenticated_client():
    """Client GraphQL sans authentification."""
    return Client()