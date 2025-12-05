import graphene
from graphene_django import DjangoObjectType
from .models import User, Playlist, PlaylistSong

class UserType(DjangoObjectType):
    playlist_count = graphene.Int()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'created_at')

    def resolve_playlist_count(self, info):
        return self.playlists.count()


class PlaylistType(DjangoObjectType):
    song_count = graphene.Int()
    total_duration = graphene.Int()

    class Meta:
        model = Playlist
        fields = ('id', 'name', 'is_public', 'created_at', 'user')

    def resolve_song_count(self, info):
        return self.playlist_songs.count()

    def resolve_total_duration(self, info):
        return sum(ps.song.duration_seconds for ps in self.playlist_songs.all())


class PlaylistSongType(DjangoObjectType):
    class Meta:
        model = PlaylistSong
        fields = ('id', 'playlist', 'song', 'position', 'added_at')
