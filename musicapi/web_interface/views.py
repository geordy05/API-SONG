from django.shortcuts import render

def index(request):
    """Page d'accueil"""
    return render(request, 'index.html')

def catalog(request):
    """Page pour explorer le catalog (REST API)"""
    return render(request, 'catalog.html')

def playlists(request):
    """Page pour gérer les playlists (GraphQL API)"""
    return render(request, 'playlists.html')
