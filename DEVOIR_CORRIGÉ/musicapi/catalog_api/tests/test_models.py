import pytest
from catalog_api.models import Artist, Album, Song

@pytest.mark.django_db
class TestCatalogModels:
    
    def test_create_artist(self):
        artist = Artist.objects.create(
            name="Daft Punk",
            country="France",
            formed_year=1993
        )
        assert artist.name == "Daft Punk"
        assert artist.country == "France"
        assert Artist.objects.filter(name="Daft Punk").exists()

    def test_create_album_and_song(self):
        # 1. Création Artiste
        artist = Artist.objects.create(name="Adele", country="UK", formed_year=2006)
        
        # 2. Création Album
        album = Album.objects.create(
            title="21", 
            artist=artist, 
            release_year=2011,
            genre="Pop"
        )
        
        # 3. Création Chanson (avec duration_seconds)
        song = Song.objects.create(
            title="Rolling in the Deep",
            album=album,
            artist=artist,
            duration_seconds=228,  # 3min 48s
            track_number=1
        )

        assert song.title == "Rolling in the Deep"
        assert song.album.title == "21"
        assert song.duration_formatted == "3:48"

@pytest.mark.django_db
class TestSongModel:
    def test_song_str_representation(self, sample_song):
        """Test de la représentation string"""
        # sample_song vient de ton conftest.py : "Money" (382s -> 6:22)
        expected = "Money (6:22)"
        assert str(sample_song) == expected
    def test_artist_str_representation(self):
            """Test de la représentation string de l'Artiste"""
            artist = Artist.objects.create(name="Sting", country="UK", formed_year=1977)
            # On suppose que __str__ renvoie le nom
            assert str(artist) == "Sting"

    def test_album_str_representation(self):
        """Test de la représentation string de l'Album"""
        artist = Artist.objects.create(name="Sting", country="UK", formed_year=1977)
        album = Album.objects.create(title="The Soul Cages", artist=artist, release_year=1991, genre="Rock")
        # On suppose que __str__ renvoie le titre (ou titre + année selon ton modèle)
        assert "The Soul Cages" in str(album)