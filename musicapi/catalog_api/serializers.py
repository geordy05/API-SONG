from rest_framework import serializers
from .models import Artist, Album, Song


class ArtistListSerializer(serializers.ModelSerializer):
    """Version simplifiée d'un artiste pour les listes"""
    album_count = serializers.ReadOnlyField()
    song_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Artist
        fields = ['id', 'name', 'country', 'formed_year', 'album_count', 'song_count']


class ArtistSerializer(serializers.ModelSerializer):
    """Détails complets de l'artiste (sans les albums imbriqués)"""
    album_count = serializers.ReadOnlyField()
    song_count = serializers.ReadOnlyField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'country', 'formed_year', 'album_count', 'song_count']


class AlbumListSerializer(serializers.ModelSerializer):
    """Version simplifiée d'un album pour les listes"""
    artist = ArtistListSerializer(read_only=True)
    song_count = serializers.ReadOnlyField()
    total_duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'release_year', 'genre', 'song_count', 'total_duration']


class AlbumSerializer(serializers.ModelSerializer):
    """Détails complets d'un album"""
    song_count = serializers.ReadOnlyField()
    total_duration = serializers.ReadOnlyField()
    artist = ArtistListSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        source='artist',
        write_only=True
    )

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'artist_id',
            'release_year', 'genre', 'song_count', 'total_duration'
        ]


class SongListSerializer(serializers.ModelSerializer):
    """Version simplifiée d'une chanson pour les listes"""
    artist = ArtistListSerializer(read_only=True)
    album = AlbumListSerializer(read_only=True)
    duration_formatted = serializers.ReadOnlyField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'album', 'duration_formatted', 'track_number']


class SongSerializer(serializers.ModelSerializer):
    """Détails complets d'une chanson"""
    duration_formatted = serializers.ReadOnlyField()
    artist = ArtistListSerializer(read_only=True)
    album = AlbumListSerializer(read_only=True)

    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        source='artist',
        write_only=True
    )
    album_id = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(),
        source='album',
        write_only=True
    )

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'artist', 'album',
            'artist_id', 'album_id',
            'duration_seconds', 'duration_formatted', 'track_number'
        ]