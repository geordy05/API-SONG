from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Artist, Album, Song
from .serializers import (
    ArtistSerializer, ArtistListSerializer,
    AlbumSerializer, AlbumListSerializer,
    SongSerializer, SongListSerializer
)
from .permissions import IsContributorOrReadOnly , IsAuthenticatedReadOnly, CreateArtistThrottle
from rest_framework import permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticatedReadOnly | IsContributorOrReadOnly]
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = ['name', 'formed_year']
    ordering = ['-formed_year']

# --- AJOUTER CE DÉCORATEUR ---
    @extend_schema(
        summary="Lister tous les artistes",
        description="Récupère une liste paginée de tous les artistes du catalogue.",
        parameters=[
            OpenApiParameter(
                name='search', 
                description='Filtre par nom d\'artiste (contient)', 
                required=False, 
                type=OpenApiTypes.STR
            )
        ],
        responses={200: ArtistSerializer(many=True)},
        tags=['Artists'] # <-- Regroupe dans l'onglet 'Artists'
    )
    def list(self, request, *args, **kwargs):
        # ... (votre logique de list existante)
        return super().list(request, *args, **kwargs)

    # --- AJOUTER CE DÉCORATEUR ---
    @extend_schema(
        summary="Créer un nouvel artiste",
        description="Ajoute un nouvel artiste à la base de données.",
        examples=[
            OpenApiExample(
                'Exemple de création',
                summary='Un artiste de rock',
                description='Exemple de body pour créer un nouvel artiste rock.',
                value={
                    "name": "The Strokes",
                    "country": "United States",
                    "formed_year": 1998
                },
                request_only=True # Cet exemple concerne la requête
            )
        ],
        responses={
            201: ArtistSerializer,
            400: OpenApiTypes.OBJECT # Pour les erreurs de validation
        },
        tags=['Artists']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    # --- AJOUTER CE DÉCORATEUR ---
    @extend_schema(
        summary="Récupérer un artiste",
        description="Récupère les détails d'un artiste spécifique par son ID.",
        responses={200: ArtistSerializer, 404: OpenApiTypes.OBJECT},
        tags=['Artists']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # --- AJOUTER CE DÉCORATEUR ---
    @extend_schema(
        summary="Mettre à jour un artiste",
        description="Met à jour complètement un artiste (PUT).",
        tags=['Artists']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    # --- AJOUTER CE DÉCORATEUR ---
    @extend_schema(
        summary="Mettre à jour partiellement un artiste",
        description="Met à jour partiellement un artiste (PATCH).",
        tags=['Artists']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    # --- AJOUTER CE DÉCORATEUR ---
    @extend_schema(
        summary="Supprimer un artiste",
        description="Supprime un artiste de la base de données.",
        responses={204: None, 404: OpenApiTypes.OBJECT},
        tags=['Artists']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # --- AJOUTER CE DÉCORATEUR (Pour vos actions custom) ---
    @extend_schema(
        summary="Lister les albums d'un artiste",
        description="Récupère la liste de tous les albums pour un artiste spécifique.",
        responses={200: AlbumSerializer(many=True)},
        tags=['Artists'] # Toujours dans le groupe 'Artists'
    )
    @action(detail=True, methods=['get'])
    def albums(self, request, pk=None):
        # ... (votre logique d'action)
        artist = self.get_object()
        albums = artist.albums.all()
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

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
    def get_throttles(self):
        """
        Applique un throttle spécifique pour l'action 'create'.
        """
        # Si l'action est 'create' (c-à-d un POST sur /artists/)
        if self.action == 'create':
            # On retourne notre classe de throttle spécifique
            return [CreateArtistThrottle()]
        
        # Pour toutes les autres actions (list, retrieve, update, delete...),
        # on utilise les throttles par défaut définis dans settings.py
        return super().get_throttles()


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