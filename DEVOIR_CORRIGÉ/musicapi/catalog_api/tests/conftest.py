import pytest
from catalog_api.models import Artist, Album, Song
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

@pytest.fixture
def authenticated_user():
    """Crée un utilisateur pour l'authentification."""
    return User.objects.create_user(
        username='authenticated_user',
        email='authenticated@example.com',
        password='testpass123'
    )
@pytest.fixture
def authenticated_client(authenticated_user):
    """Client API REST authentifié avec JWT."""
    client = APIClient()
    refresh = RefreshToken.for_user(authenticated_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client

@pytest.fixture
def unauthenticated_client():
    """Client API REST sans authentification."""
    return APIClient()

@pytest.fixture
def sample_artist():
    """Crée un artiste de test"""
    return Artist.objects.create(
        name="Pink Floyd",
        country="UK",
        formed_year=1965
    )

@pytest.fixture
def sample_album(sample_artist):
    """Crée un album de test"""
    return Album.objects.create(
        title="The Dark Side of the Moon",
        artist=sample_artist,
        release_year=1973,
        genre="Progressive Rock"
    )


@pytest.fixture
def sample_song(sample_artist, sample_album):
    """Crée une chanson de test"""
    return Song.objects.create(
        title="Money",
        artist=sample_artist,
        album=sample_album,
        duration_seconds=382,
        track_number=6
    )

@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()