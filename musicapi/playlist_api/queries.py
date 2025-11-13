import graphene
from .types import UserType, PlaylistType
from .models import User, Playlist

class Query(graphene.ObjectType):

    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    all_playlists = graphene.List(PlaylistType)
    playlist = graphene.Field(PlaylistType, id=graphene.Int(required=True))
    public_playlists = graphene.List(PlaylistType)
    playlists_by_user = graphene.List(PlaylistType, user_id=graphene.Int(required=True))
    def resolve_all_users(root, info):
        return User.objects.prefetch_related('playlists').all()

    def resolve_user(root, info, id):
        try:
            return User.objects.prefetch_related('playlists').get(id=id)
        except User.DoesNotExist:
            return None

    def resolve_all_playlists(root, info):
        return Playlist.objects.select_related('user').prefetch_related('playlist_songs__song').all()

    def resolve_playlist(root, info, id):
        try:
            return Playlist.objects.select_related('user').prefetch_related('playlist_songs__song').get(id=id)
        except Playlist.DoesNotExist:
            return None

    def resolve_public_playlists(root, info):
        return Playlist.objects.filter(is_public=True).select_related('user').prefetch_related('playlist_songs__song')

    def resolve_playlists_by_user(root, info, user_id):
        return Playlist.objects.filter(user_id=user_id).select_related('user').prefetch_related('playlist_songs__song')
