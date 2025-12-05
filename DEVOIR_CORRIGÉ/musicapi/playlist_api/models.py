from django.db import models
from catalog_api.models import Song 


class User(models.Model):
    username = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_user'
        managed = True
    
    def __str__(self):
        return self.username

    @property
    def playlist_count(self):
        """Nombre total de playlists associées à cet utilisateur"""
        return self.playlists.count()


class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        db_column='user_id' 
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = 'playlist'
        managed = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def song_count(self):
        """Nombre de chansons dans la playlist"""
        return self.playlist_songs.count()

    @property
    def total_duration(self):
        """Durée totale de toutes les chansons (en secondes)"""
        total = sum(ps.song.duration_seconds for ps in self.playlist_songs.all())
        return total


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='playlist_songs',
        db_column='playlist_id'
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='playlist_songs',
        db_column='song_id'  
    )
    position = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'playlist_song' 
        managed = True
        unique_together = [['playlist', 'song']]
        ordering = ['position']

    def __str__(self):
        return f"{self.song.title} → {self.playlist.name} (#{self.position})"