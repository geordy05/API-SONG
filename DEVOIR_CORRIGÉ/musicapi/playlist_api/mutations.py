import graphene
from django.db.models import Max
from django.db import transaction
from .types import PlaylistType
# Import 'User' de playlist_api en tant que 'AppUser'
from .models import User as AppUser, Playlist, PlaylistSong 
from catalog_api.models import Song
from graphql import GraphQLError

# Importer nos nouveaux outils de sécurité
from .decorators import oauth2_required
from .utils import get_or_create_app_user_from_info
# 'AccessToken' n'est plus nécessaire ici


class CreatePlaylist(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        is_public = graphene.Boolean(default_value=False)

    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @oauth2_required  # <- 1. On applique le décorateur
    def mutate(self, info, name, is_public=False):
        # 2. TOUT le code manuel de vérification du token a été SUPPRIMÉ
        
        try:            
            # 3. On utilise notre fonction 'pont'
            app_user = get_or_create_app_user_from_info(info)
            playlist = Playlist.objects.create(
                name=name,
                user=app_user, # 4. On utilise l'utilisateur mappé
                is_public = is_public
            )
            return CreatePlaylist(playlist=playlist, success=True, errors=[])
        except GraphQLError as e:
            return CreatePlaylist(success=False, errors=[str(e)])
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

    @oauth2_required
    def mutate(self, info, id, name=None, is_public=None):
        try:
            app_user = get_or_create_app_user_from_info(info)
            playlist = Playlist.objects.get(pk=id)
            

            if playlist.user != app_user:
                raise GraphQLError("Vous n'êtes pas le propriétaire de cette playlist")

            if name is not None:
                playlist.name = name
            if is_public is not None:
                playlist.is_public = is_public
            
            playlist.save()
            return UpdatePlaylist(playlist=playlist, success=True, errors=[])

        except Playlist.DoesNotExist:
            return UpdatePlaylist(success=False, errors=["Playlist not found"])
        except GraphQLError as e:
            return UpdatePlaylist(success=False, errors=[str(e)])
        except Exception as e:
            return UpdatePlaylist(success=False, errors=[f"Error updating playlist: {str(e)}"])


class DeletePlaylist(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @oauth2_required # <- SÉCURITÉ AJOUTÉE
    def mutate(self, info, id):
        try:
            app_user = get_or_create_app_user_from_info(info)
            playlist = Playlist.objects.get(pk=id)

            # ----------------------------------------------
            # VÉRIFICATION DE PROPRIÉTÉ
            # ----------------------------------------------
            if playlist.user != app_user:
                raise GraphQLError("Vous n'êtes pas le propriétaire de cette playlist")

            playlist.delete()
            return DeletePlaylist(success=True, errors=[])

        except Playlist.DoesNotExist:
            return DeletePlaylist(success=False, errors=["Playlist not found"])
        except GraphQLError as e:
            return DeletePlaylist(success=False, errors=[str(e)])
        except Exception as e:
            return DeletePlaylist(success=False, errors=[f"Error deleting playlist: {str(e)}"])


class AddSongToPlaylist(graphene.Mutation):
    class Arguments:
        playlist_id = graphene.Int(required=True)
        song_id = graphene.Int(required=True)

    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @oauth2_required # <- SÉCURITÉ AJOUTÉE
    def mutate(self, info, playlist_id, song_id):
        try:
            app_user = get_or_create_app_user_from_info(info)
            playlist = Playlist.objects.get(pk=playlist_id)

            # ----------------------------------------------
            # VÉRIFICATION DE PROPRIÉTÉ
            # ----------------------------------------------
            if playlist.user != app_user:
                raise GraphQLError("Vous ne pouvez ajouter des chansons qu'à vos propres playlists")

            try:
                song = Song.objects.get(pk=song_id)
            except Song.DoesNotExist:
                return AddSongToPlaylist(success=False, errors=["Song not found"])
            
            if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                return AddSongToPlaylist(success=False, errors=["Song already in playlist"])
            
            # ... (votre logique de position est conservée)
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
            return AddSongToPlaylist(success=False, errors=["Playlist not found"])
        except GraphQLError as e:
            return AddSongToPlaylist(success=False, errors=[str(e)])
        except Exception as e:
            return AddSongToPlaylist(success=False, errors=[f"Error adding song: {str(e)}"])


class RemoveSongFromPlaylist(graphene.Mutation):
    class Arguments:
        playlist_id = graphene.Int(required=True)
        song_id = graphene.Int(required=True)

    playlist = graphene.Field(PlaylistType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @oauth2_required # <- SÉCURITÉ AJOUTÉE
    def mutate(self, info, playlist_id, song_id):
        try:
            app_user = get_or_create_app_user_from_info(info)
            playlist = Playlist.objects.get(pk=playlist_id)

            # ----------------------------------------------
            # VÉRIFICATION DE PROPRIÉTÉ
            # ----------------------------------------------
            if playlist.user != app_user:
                raise GraphQLError("Vous ne pouvez retirer des chansons que de vos propres playlists")

            try:
                playlist_song = PlaylistSong.objects.get(
                    playlist_id=playlist_id, 
                    song_id=song_id
                )
                playlist_song.delete()
            except PlaylistSong.DoesNotExist:
                return RemoveSongFromPlaylist(success=False, errors=["Song not in playlist"])
            
            # ... (votre logique de ré-indexation est conservée)
            for idx, ps in enumerate(
                PlaylistSong.objects.filter(playlist_id=playlist_id).order_by('position'), 
                start=1
            ):
                ps.position = idx
                ps.save()

            return RemoveSongFromPlaylist(playlist=playlist, success=True, errors=[])
            
        except Playlist.DoesNotExist:
            return RemoveSongFromPlaylist(success=False, errors=["Playlist not found"])
        except GraphQLError as e:
            return RemoveSongFromPlaylist(success=False, errors=[str(e)])
        except Exception as e:
            return RemoveSongFromPlaylist(success=False, errors=[f"Error removing song: {str(e)}"])


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

    @oauth2_required # <- SÉCURITÉ AJOUTÉE
    def mutate(self, info, playlist_id, song_positions):
        try:
            app_user = get_or_create_app_user_from_info(info)
            playlist = Playlist.objects.get(pk=playlist_id)

            # ----------------------------------------------
            # VÉRIFICATION DE PROPRIÉTÉ
            # ----------------------------------------------
            if playlist.user != app_user:
                raise GraphQLError("Vous ne pouvez réorganiser que vos propres playlists")

            with transaction.atomic():
                for sp in song_positions:
                    try:
                        ps = PlaylistSong.objects.get(
                            playlist=playlist, 
                            song_id=sp.song_id
                        )
                        ps.position = sp.position
                        ps.save()
                    except PlaylistSong.objects.get(pk=id).DoesNotExist:
                        return ReorderPlaylistSongs(
                            success=False, 
                            errors=[f"Song {sp.song_id} not in playlist"]
                        )

            return ReorderPlaylistSongs(playlist=playlist, success=True, errors=[])
            
        except Playlist.DoesNotExist:
            return ReorderPlaylistSongs(success=False, errors=["Playlist not found"])
        except GraphQLError as e:
            return ReorderPlaylistSongs(success=False, errors=[str(e)])
        except Exception as e:
            return ReorderPlaylistSongs(success=False, errors=[f"Error reordering songs: {str(e)}"])


# Votre classe Mutation principale reste inchangée
class Mutation(graphene.ObjectType):
    create_playlist = CreatePlaylist.Field()
    update_playlist = UpdatePlaylist.Field()
    delete_playlist = DeletePlaylist.Field()
    add_song_to_playlist = AddSongToPlaylist.Field()
    remove_song_from_playlist = RemoveSongFromPlaylist.Field()