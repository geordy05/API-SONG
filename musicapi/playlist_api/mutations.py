import graphene
from django.db.models import Max
from django.db import transaction
from .types import PlaylistType
from .models import User, Playlist, PlaylistSong
from catalog_api.models import Song
from graphql import GraphQLError
from oauth2_provider.models import AccessToken


class CreatePlaylist(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        is_public = graphene.Boolean(default_value=False)
    
    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, name, is_public=False):
        # Récupérer le token depuis le header
        request = info.context
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            raise GraphQLError("Authentication required")
        
        token_str = auth_header.split(' ')[1]
        
        try:
            token = AccessToken.objects.get(token=token_str)
            
            # Vérifier que le token n'a pas expiré
            if token.is_expired():
                raise GraphQLError("Token expired")
            
            # Attacher l'utilisateur au contexte
            request.user = token.user
            
        except AccessToken.DoesNotExist:
            raise GraphQLError("Invalid token")
        
        try:            
            user = User.objects.get(username=token.user)
            playlist = Playlist.objects.create(
                name=name,
                user=user,
                is_public=is_public
            )
            return CreatePlaylist(playlist=playlist, success=True, errors=[])
        except User.DoesNotExist:
            return CreatePlaylist(
                success=False,
                errors=[f"Utilisateur {token.user} non trouvé dans app_user"]
            )
        except Exception as e:
            return CreatePlaylist(
                success=False,
                errors=[str(e)]
            )


class UpdatePlaylist(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        is_public = graphene.Boolean()

    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, name=None, is_public=None):
        try:
            playlist = Playlist.objects.get(pk=id)
            
            if name is not None:
                playlist.name = name
            if is_public is not None:
                playlist.is_public = is_public
            
            playlist.save()
            return UpdatePlaylist(playlist=playlist, success=True, errors=[])
        except Playlist.DoesNotExist:
            return UpdatePlaylist(
                playlist=None, 
                success=False, 
                errors=["Playlist not found"]
            )
        except Exception as e:
            return UpdatePlaylist(
                playlist=None, 
                success=False, 
                errors=[f"Error updating playlist: {str(e)}"]
            )


class DeletePlaylist(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        try:
            playlist = Playlist.objects.get(pk=id)
            playlist.delete()
            return DeletePlaylist(success=True, errors=[])
        except Playlist.DoesNotExist:
            return DeletePlaylist(
                success=False, 
                errors=["Playlist not found"]
            )
        except Exception as e:
            return DeletePlaylist(
                success=False, 
                errors=[f"Error deleting playlist: {str(e)}"]
            )


class AddSongToPlaylist(graphene.Mutation):
    class Arguments:
        playlist_id = graphene.Int(required=True)
        song_id = graphene.Int(required=True)

    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, playlist_id, song_id):
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
            try:
                song = Song.objects.get(pk=song_id)
            except Song.DoesNotExist:
                return AddSongToPlaylist(
                    playlist=None, 
                    success=False, 
                    errors=["Song not found"]
                )
            if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                return AddSongToPlaylist(
                    playlist=None, 
                    success=False, 
                    errors=["Song already in playlist"]
                )
            
            agg = PlaylistSong.objects.filter(playlist=playlist).aggregate(
                max_position=Max('position')
            )
            last_position = agg['max_position'] or 0
            position = last_position + 1

            PlaylistSong.objects.create(
                playlist=playlist, 
                song=song, 
                position=position
            )
            
            return AddSongToPlaylist(playlist=playlist, success=True, errors=[])
            
        except Playlist.DoesNotExist:
            return AddSongToPlaylist(
                playlist=None, 
                success=False, 
                errors=["Playlist not found"]
            )
        except Exception as e:
            return AddSongToPlaylist(
                playlist=None, 
                success=False, 
                errors=[f"Error adding song to playlist: {str(e)}"]
            )


class RemoveSongFromPlaylist(graphene.Mutation):
    class Arguments:
        playlist_id = graphene.Int(required=True)
        song_id = graphene.Int(required=True)

    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, playlist_id, song_id):
        try:
            playlist = Playlist.objects.get(pk=playlist_id)

            try:
                playlist_song = PlaylistSong.objects.get(
                    playlist_id=playlist_id, 
                    song_id=song_id
                )
                playlist_song.delete()
            except PlaylistSong.DoesNotExist:
                return RemoveSongFromPlaylist(
                    playlist=None, 
                    success=False, 
                    errors=["Song not in playlist"]
                )
            
           
            for idx, ps in enumerate(
                PlaylistSong.objects.filter(playlist_id=playlist_id).order_by('position'), 
                start=1
            ):
                ps.position = idx
                ps.save()

            return RemoveSongFromPlaylist(playlist=playlist, success=True, errors=[])
            
        except Playlist.DoesNotExist:
            return RemoveSongFromPlaylist(
                playlist=None, 
                success=False, 
                errors=["Playlist not found"]
            )
        except Exception as e:
            return RemoveSongFromPlaylist(
                playlist=None, 
                success=False, 
                errors=[f"Error removing song from playlist: {str(e)}"]
            )


class SongPositionInput(graphene.InputObjectType):
    song_id = graphene.Int(required=True)
    position = graphene.Int(required=True)


class ReorderPlaylistSongs(graphene.Mutation):
    class Arguments:
        playlist_id = graphene.Int(required=True)
        song_positions = graphene.List(SongPositionInput, required=True)

    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, playlist_id, song_positions):
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
            with transaction.atomic():
                for sp in song_positions:
                    try:
                        ps = PlaylistSong.objects.get(
                            playlist=playlist, 
                            song_id=sp.song_id
                        )
                        ps.position = sp.position
                        ps.save()
                    except PlaylistSong.DoesNotExist:
                        return ReorderPlaylistSongs(
                            playlist=None, 
                            success=False, 
                            errors=[f"Song {sp.song_id} not in playlist"]
                        )

            return ReorderPlaylistSongs(playlist=playlist, success=True, errors=[])
            
        except Playlist.DoesNotExist:
            return ReorderPlaylistSongs(
                playlist=None, 
                success=False, 
                errors=["Playlist not found"]
            )
        except Exception as e:
            return ReorderPlaylistSongs(
                playlist=None, 
                success=False, 
                errors=[f"Error reordering songs: {str(e)}"]
            )


class Mutation(graphene.ObjectType):
    create_playlist = CreatePlaylist.Field()
    update_playlist = UpdatePlaylist.Field()
    delete_playlist = DeletePlaylist.Field()
    add_song_to_playlist = AddSongToPlaylist.Field()
    remove_song_from_playlist = RemoveSongFromPlaylist.Field()
    reorder_playlist_songs = ReorderPlaylistSongs.Field()