import pytest
from graphene.test import Client
from musicapi_project.schema import schema
from playlist_api.models import Playlist, User as AppUser
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.models import AnonymousUser
from oauth2_provider.models import AccessToken, Application
from django.utils import timezone
from datetime import timedelta

class MockContext:
    def __init__(self, user=None):
        self.user = user or AnonymousUser()
        self.META = {}
        self.method = 'POST'
        
        # Django sait tout seul que user.is_authenticated est True pour un vrai user
        if self.user.is_authenticated:
            app, _ = Application.objects.get_or_create(
                name="Test App",
                client_type=Application.CLIENT_PUBLIC,
                authorization_grant_type=Application.GRANT_PASSWORD,
            )
            token_string = "token_valide_pour_le_test"
            
            AccessToken.objects.get_or_create(
                user=self.user,
                application=app,
                token=token_string,
                defaults={
                    'expires': timezone.now() + timedelta(hours=1),
                    'scope': 'read write'
                }
            )
            self.META['HTTP_AUTHORIZATION'] = f"Bearer {token_string}"

@pytest.fixture
def auth_user(db):
    """Utilisateur pour l'authentification (table auth_user)"""
    return AuthUser.objects.create_user(username='test_user', password='password', email='test@example.com')

@pytest.fixture
def app_user(db, auth_user):
    """Utilisateur métier (table app_user), lié par le même username"""
    return AppUser.objects.create(username=auth_user.username, email=auth_user.email)

@pytest.fixture
def sample_playlist(db, app_user):
    """Playlist liée à l'utilisateur métier"""
    return Playlist.objects.create(name="My Awesome Playlist", user=app_user)

@pytest.mark.django_db
class TestPlaylistQueries:
    
    def test_all_playlists_query(self, auth_user, app_user, sample_playlist):
        # On ne touche plus à is_authenticated, c'est automatique
        context = MockContext(user=auth_user)
        client = Client(schema)
        
        query = '''
            query {
                allPlaylists {
                    id
                    name
                    isPublic
                    user {
                        username
                    }
                }
            }
        '''
        result = client.execute(query, context=context)
        
        assert 'errors' not in result
        assert len(result['data']['allPlaylists']) == 1
        assert result['data']['allPlaylists'][0]['name'] == "My Awesome Playlist"
        assert result['data']['allPlaylists'][0]['user']['username'] == app_user.username
    
    def test_public_playlists_query(self, app_user):
        Playlist.objects.create(name="Public 1", user=app_user, is_public=True)
        Playlist.objects.create(name="Private 1", user=app_user, is_public=False)
        
        # Contexte anonyme
        context = MockContext(user=None)
        client = Client(schema)
        
        query = '''
            query {
                publicPlaylists {
                    name
                    isPublic
                }
            }
        '''
        result = client.execute(query, context=context)
        
        assert 'errors' not in result
        assert len(result['data']['publicPlaylists']) == 1
        assert result['data']['publicPlaylists'][0]['name'] == "Public 1"

@pytest.mark.django_db
class TestPlaylistMutations:
    
    def test_create_playlist_mutation(self, auth_user, app_user):
        context = MockContext(user=auth_user)
        client = Client(schema)
        
        mutation = '''
            mutation {
                createPlaylist(
                    name: "New Playlist"
                    isPublic: true
                ) {
                    success
                    playlist {
                        name
                        isPublic
                    }
                }
            }
        '''
        result = client.execute(mutation, context=context)
        
        assert 'errors' not in result
        assert result['data']['createPlaylist']['success'] is True
        assert result['data']['createPlaylist']['playlist']['name'] == "New Playlist"
    
    def test_update_playlist_mutation(self, auth_user, sample_playlist):
        context = MockContext(user=auth_user)
        client = Client(schema)
        
        mutation = '''
            mutation {
                updatePlaylist(
                    id: %d
                    name: "Updated Name"
                ) {
                    success
                    playlist {
                        name
                    }
                }
            }
        ''' % sample_playlist.id
        
        result = client.execute(mutation, context=context)
        
        assert 'errors' not in result
        assert result['data']['updatePlaylist']['success'] is True
        assert result['data']['updatePlaylist']['playlist']['name'] == "Updated Name"