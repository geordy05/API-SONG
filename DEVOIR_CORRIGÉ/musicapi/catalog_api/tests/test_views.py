import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from catalog_api.models import Artist
import uuid

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(django_user_model):
    """Crée un admin unique"""
    username = f'admin_{uuid.uuid4()}'
    return django_user_model.objects.create_superuser(
        username=username, 
        password='password', 
        email=f'{username}@test.com'
    )

@pytest.mark.django_db
class TestArtistViewSet:
    
    def test_list_artists(self, api_client, sample_artist, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('artist-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) >= 1
    
    def test_retrieve_artist(self, api_client, sample_artist, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('artist-detail', kwargs={'pk': sample_artist.id})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == "Pink Floyd"
    
    def test_create_artist(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('artist-list')
        data = {'name': 'Led Zeppelin', 'country': 'UK', 'formed_year': 1968}
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        assert response.data['name'] == 'Led Zeppelin'
    
    def test_delete_artist(self, api_client, sample_artist, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('artist-detail', kwargs={'pk': sample_artist.id})
        response = api_client.delete(url)
        assert response.status_code == 204
        assert not Artist.objects.filter(id=sample_artist.id).exists()

    def test_update_artist(self, api_client, sample_artist, admin_user):
        """Test de mise à jour d'un artiste"""
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('artist-detail', kwargs={'pk': sample_artist.id})
        data = {
            'name': 'Pink Floyd Updated',
            'country': 'UK',
            'formed_year': 1965
        }
        
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == 200
        assert response.data['name'] == "Pink Floyd Updated"
        # On vérifie en base que ça a bien changé
        sample_artist.refresh_from_db()
        assert sample_artist.name == "Pink Floyd Updated"