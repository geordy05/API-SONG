import pytest
from playlist_api.models import Playlist, User # Import du modèle local
from catalog_api.models import Artist, Album, Song

@pytest.mark.django_db
class TestPlaylistModel:
    
    def test_create_playlist_with_songs(self):
        """Test de création d'une playlist avec des chansons"""
        # 1. Créer un utilisateur (Table app_user)
        user = User.objects.create(
            username='music_fan', 
            email='fan@music.com'
        )
        
        # 2. Créer des données musicales
        artist = Artist.objects.create(name="Sting", country="UK", formed_year=1977)
        album = Album.objects.create(title="Ten Summoner's Tales", artist=artist, release_year=1993, genre="Pop")
        # Note: Song attend duration_seconds (int) selon votre code précédent
        song = Song.objects.create(
            title="Shape of My Heart", 
            album=album, 
            artist=artist, 
            duration_seconds=240, 
            track_number=10
        )

        # 3. Créer la playlist
        # Ici on peut passer l'objet 'user' directement car c'est la bonne classe !
        playlist = Playlist.objects.create(name="Ma Playlist Cool", user=user)
        
        # On passe par le modèle intermédiaire PlaylistSong si le ManyToMany n'est pas direct
        # D'après votre modèle, vous n'avez pas de champ ManyToMany direct 'songs' dans Playlist,
        # mais une table intermédiaire PlaylistSong. Il faut donc créer l'objet intermédiaire.
        from playlist_api.models import PlaylistSong
        PlaylistSong.objects.create(playlist=playlist, song=song)

        assert playlist.name == "Ma Playlist Cool"
        # On vérifie via la relation related_name='playlist_songs'
        assert playlist.playlist_songs.count() == 1
        assert playlist.playlist_songs.first().song.title == "Shape of My Heart"

    def test_playlist_str_representation(self, sample_playlist):
        """Test de __str__"""
        # Votre modèle renvoie : f"{self.name} ({self.user.username})"
        expected = f"{sample_playlist.name} ({sample_playlist.user.username})"
        assert str(sample_playlist) == expected
    
    def test_playlist_song_count_property(self):
        """Test de la propriété song_count"""
        user = User.objects.create(username='count_user', email='count@test.com')
        playlist = Playlist.objects.create(name="Count Test", user=user)
        
        # On ne met aucune chanson au début
        assert playlist.song_count == 0
        
        # On ajoute une chanson (via la table intermédiaire si nécessaire, ou direct si tu as adapté)
        # Supposons ici que tu as besoin de créer la relation
        from playlist_api.models import PlaylistSong
        artist = Artist.objects.create(name="TestArtist", country="FR", formed_year=2020)
        album = Album.objects.create(title="TestAlbum", artist=artist, release_year=2020, genre="Pop")
        song = Song.objects.create(title="TestSong", album=album, artist=artist, duration_seconds=120, track_number=1)
        
        PlaylistSong.objects.create(playlist=playlist, song=song)
        
        # On recharge pour être sûr
        assert playlist.playlist_songs.count() == 1
        assert playlist.song_count == 1

    def test_playlist_total_duration_property(self):
        """Test de la propriété total_duration (somme des secondes)"""
        user = User.objects.create(username='duration_user', email='duration@test.com')
        playlist = Playlist.objects.create(name="Duration Test", user=user)
        
        artist = Artist.objects.create(name="Artist2", country="US", formed_year=2021)
        album = Album.objects.create(title="Album2", artist=artist, release_year=2021, genre="Rock")
        
        # Chanson 1 : 100 secondes
        song1 = Song.objects.create(title="S1", album=album, artist=artist, duration_seconds=100, track_number=1)
        # Chanson 2 : 200 secondes
        song2 = Song.objects.create(title="S2", album=album, artist=artist, duration_seconds=200, track_number=2)
        
        from playlist_api.models import PlaylistSong
        PlaylistSong.objects.create(playlist=playlist, song=song1)
        PlaylistSong.objects.create(playlist=playlist, song=song2)
        
        # Total attendu : 100 + 200 = 300
        assert playlist.total_duration == 300