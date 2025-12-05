from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    formed_year = models.IntegerField()
    
    class Meta:
        db_table = 'artist'
        managed = True

    @property
    def album_count(self):
        """Nombre total d'albums de l'artiste"""
        return self.albums.count()
    
    @property
    def song_count(self):
        """Nombre total de chansons de l'artiste"""
        return self.songs.count()
    
    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE, 
        related_name='albums', 
        db_column='artist_id'
    )
    release_year = models.IntegerField()
    genre = models.CharField(max_length=100)

    class Meta:
        db_table = 'album'
        managed = True
    
    @property
    def song_count(self):
        """Nombre total de chansons dans l'album"""
        return self.songs.count()
    
    @property
    def total_duration(self):
        """Durée totale de l'album en secondes"""
        return sum(song.duration_seconds for song in self.songs.all())
    
    def __str__(self):
        return f"{self.title} ({self.release_year})"

    
class Song(models.Model):
    title = models.CharField(max_length=200)
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='songs',
        db_column='album_id'
    )
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='songs',
        db_column='artist_id'
    )
    duration_seconds = models.IntegerField()
    track_number = models.IntegerField()

    class Meta:
        db_table = 'song'
        managed = True
        ordering = ['album', 'track_number']

    @property
    def duration_formatted(self):
        """Durée formatée en minutes et secondes (MM:SS)"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def __str__(self):
        return f"{self.title} ({self.duration_formatted})"