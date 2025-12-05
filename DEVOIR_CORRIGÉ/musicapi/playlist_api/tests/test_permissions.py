import pytest
import json

@pytest.mark.django_db
def test_allPlaylists_with_authentication(authenticated_client):
    """Teste la récupération de toutes les playlists avec authentification."""
    query = """
            query {
                allPlaylists {
                    id
                    name
                    isPublic
                    songCount
                }
            }
        """

    response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query}),
            content_type='application/json',
        )
    assert response.status_code == 200

@pytest.mark.django_db
def test_allPlaylists_without_authentication(unauthenticated_client):
    """Teste la récupération de toutes les playlists sans authentification."""
    query = """
            query {
                allPlaylists {
                    id
                    name
                    isPublic
                    songCount
                }
            }
        """

    response = unauthenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query}),
            content_type='application/json',
        )
    assert response.status_code == 403  # Unauthorized