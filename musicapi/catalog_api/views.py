from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Artist, Album, Song
from .serializers import (
    ArtistSerializer, ArtistListSerializer,
    AlbumSerializer, AlbumListSerializer,
    SongSerializer, SongListSerializer
)
from .permissions import IsContributorOrReadOnly , IsAuthenticatedReadOnly

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticatedReadOnly | IsContributorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = ['name', 'formed_year']
    ordering = ['-formed_year']

    def get_serializer_class(self):
        if self.action == 'list':
            return ArtistListSerializer
        return ArtistSerializer

    @action(detail=True, methods=['get'])
    def albums(self, request, pk=None):
        """Retourne tous les albums de l'artiste"""
        artist = self.get_object()
        albums = artist.albums.all()
        serializer = AlbumListSerializer(albums, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        """Retourne toutes les chansons de l'artiste"""
        artist = self.get_object()
        songs = artist.songs.all()
        serializer = SongListSerializer(songs, many=True)
        return Response(serializer.data)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.select_related('artist').all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticatedReadOnly | IsContributorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'artist__name', 'genre']
    ordering_fields = ['title', 'release_year']
    ordering = ['-release_year']

    def get_serializer_class(self):
        if self.action == 'list':
            return AlbumListSerializer
        return AlbumSerializer

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        """Retourne toutes les chansons de l'album triées par track_number"""
        album = self.get_object()
        songs = album.songs.all().order_by('track_number')
        serializer = SongListSerializer(songs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """Filtre les albums par genre (query param)"""
        genre = request.query_params.get('genre', None)
        if genre:
            albums = Album.objects.filter(genre__icontains=genre).select_related('artist')
            serializer = AlbumListSerializer(albums, many=True)
            return Response(serializer.data)
        return Response({'error': 'Genre parameter is required'}, status=400)


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.select_related('artist', 'album').all()
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticatedReadOnly | IsContributorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'artist__name', 'album__title']
    ordering_fields = ['title', 'duration_seconds', 'track_number']
    ordering = ['album', 'track_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return SongListSerializer
        return SongSerializer