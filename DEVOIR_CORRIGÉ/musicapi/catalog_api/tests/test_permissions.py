import pytest

@pytest.mark.django_db
def test_get_artists_with_authentication(authenticated_client):
    """Teste la récupération de la liste des artistes avec authentification."""
    response = authenticated_client.get('/api/catalog/artists/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_artists_without_authentication(unauthenticated_client):
    """Teste la récupération de la liste des artistes sans authentification."""
    response = unauthenticated_client.get('/api/catalog/artists/')
    assert response.status_code == 401  # Unauthorized

@pytest.mark.django_db
def test_create_artist_without_authentication(unauthenticated_client):
    """Teste qu'on ne peut pas CRÉER un artiste sans être connecté."""
    data = {'name': 'Hacker Band', 'country': 'Unknown', 'formed_year': 2024}
    # Note: On suppose que l'URL est /api/catalog/artists/
    response = unauthenticated_client.post('/api/catalog/artists/', data)
    assert response.status_code == 401

@pytest.mark.django_db
def test_delete_artist_without_authentication(unauthenticated_client, sample_artist):
    """Teste qu'on ne peut pas SUPPRIMER un artiste sans être connecté."""
    url = f'/api/catalog/artists/{sample_artist.id}/'
    response = unauthenticated_client.delete(url)
    assert response.status_code == 401

@pytest.mark.django_db
def test_update_artist_without_authentication(unauthenticated_client, sample_artist):
    """Teste qu'on ne peut pas MODIFIER un artiste sans être connecté."""
    url = f'/api/catalog/artists/{sample_artist.id}/'
    data = {'name': 'Hacked Name'}
    response = unauthenticated_client.patch(url, data)
    assert response.status_code == 401