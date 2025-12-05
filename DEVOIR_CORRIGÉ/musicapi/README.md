# MusicAPI Project

Une API REST complète pour la gestion d'un catalogue musical avec authentification JWT et une API GraphQL pour la gestion des playlists. Le projet combine Django REST Framework avec GraphQL pour offrir deux interfaces flexibles d'accès aux données.

## 📋 Table des matières

- [Installation](#-installation)
- [Authentification JWT](#-authentification-jwt)
- [Tests](#-tests)
- [Architecture](#-architecture)

---

## 🚀 Installation

### Prérequis

- **Python** 3.10+
- **PostgreSQL** 15+
- **pip** ou **poetry** (gestionnaire de paquets Python)
- **Git**

### Étapes d'installation

#### 1. Cloner le repository

```bash
git clone <url-du-repository>
cd musicapi
```

#### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Configuration de la base de données

Le projet utilise PostgreSQL. Assurez-vous que votre serveur PostgreSQL est en cours d'exécution et que la base de données `musicdb` existe.

**Éditer `musicapi_project/settings.py`** si nécessaire :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'musicdb',
        'USER': 'musicapi',
        'PASSWORD': 'musicpass123',
        'HOST': 'localhost',  # Remplacer par votre hôte
        'PORT': '5432',        # Remplacer par votre port
    }
}
```

#### 5. Appliquer les migrations

```bash
python manage.py migrate
```

#### 6. Créer un superutilisateur (administrateur)

```bash
python manage.py createsuperuser
```

#### 7. Créer le groupe « Contributeurs »

```bash
python manage.py shell
```

Puis dans l'interpréteur Python :

```python
from django.contrib.auth.models import Group
Group.objects.create(name='Contributeurs')
exit()
```

#### 8. Lancer le serveur de développement

```bash
python manage.py runserver
```

Le serveur démarre sur `http://127.0.0.1:8000/`

---

## 🔐 Authentification JWT

Le projet utilise **JWT (JSON Web Token)** pour l'authentification via Django REST Framework Simple JWT.

### Obtenir un token JWT

#### 1. Accéder à l'endpoint d'authentification

Pour obtenir un token, effectuez une requête POST à l'endpoint suivant :

```
POST /api/token/
```

**Payload (JSON) :**

```json
{
    "username": "votre_nom_utilisateur",
    "password": "votre_mot_de_passe"
}
```

**Réponse (200 OK) :**

```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 2. Utiliser le token dans les requêtes

Ajoutez le token d'accès dans le header `Authorization` de chaque requête :

```
Authorization: Bearer <your_access_token>
```

**Exemple avec cURL :**

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:8000/api/catalog/artists/
```

**Exemple avec Python (requests) :**

```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get('http://localhost:8000/api/catalog/artists/', headers=headers)
print(response.json())
```

### Rafraîchir le token

Les tokens d'accès expirent après **60 minutes**. Pour obtenir un nouveau token, utilisez le token de rafraîchissement :

```
POST /api/token/refresh/
```

**Payload :**

```json
{
    "refresh": "votre_refresh_token"
}
```

**Réponse :**

```json
{
    "access": "nouveau_access_token"
}
```

### Permissions

- **Lecture (GET)** : Tous les utilisateurs authentifiés
- **Écriture (POST/PUT/DELETE)** : Administrateurs ou membres du groupe « Contributeurs »
- **Endpoints publics** : Certains endpoints REST permettent la lecture publique (configuration par vue)

### Durée de vie des tokens

- **Access Token** : 60 minutes
- **Refresh Token** : 24 heures

---

## 🧪 Tests

Le projet utilise **pytest** avec le plugin pytest-django et la couverture de code via pytest-cov.

### Configuration des tests

Le fichier `pytest.ini` est configuré pour :

- Module Django : `musicapi_project.settings`
- Couverture : `catalog_api` et `playlist_api`
- Rapports de couverture détaillés (terme manquant)

### Lancer les tests

#### Exécuter tous les tests

```bash
pytest
```

#### Exécuter les tests d'une application spécifique

```bash
pytest catalog_api/tests/
pytest playlist_api/tests/
```

#### Exécuter un fichier de test spécifique

```bash
pytest catalog_api/tests/test_models.py
pytest catalog_api/tests/test_views.py
pytest catalog_api/tests/test_permissions.py
```

#### Exécuter un test spécifique par son nom

```bash
pytest catalog_api/tests/test_models.py::TestArtistModel::test_artist_creation
```

### Couverture de code

#### Générer un rapport de couverture

```bash
pytest --cov=catalog_api --cov=playlist_api --cov-report=html
```

Cela crée un dossier `htmlcov/` avec un rapport interactif. Ouvrez `htmlcov/index.html` dans votre navigateur.

#### Voir la couverture en terminal

```bash
pytest --cov=catalog_api --cov=playlist_api --cov-report=term-missing
```

### Structure des tests

Les tests sont organisés par application :

```
catalog_api/tests/
├── conftest.py          # Configuration pytest (fixtures)
├── test_models.py       # Tests des modèles
├── test_views.py        # Tests des endpoints REST
└── test_permissions.py  # Tests des permissions

playlist_api/tests/
├── conftest.py
├── test_models.py
├── test_schema.py       # Tests du schéma GraphQL
└── test_permissions.py
```

### Exemples de tests

**Tests des modèles (`test_models.py`) :**
- Création d'artistes, albums, chansons
- Validation des champs
- Relations entre modèles

**Tests des vues (`test_views.py`) :**
- Endpoints REST (GET, POST, PUT, DELETE)
- Filtrage et recherche
- Pagination

**Tests des permissions (`test_permissions.py`) :**
- Accès authentifié vs anonyme
- Permissions des contributeurs
- Throttling (rate limiting)

### Couverture actuelle

Le projet vise une couverture minimale de **80%** pour les applications critiques.

Pour vérifier la couverture détaillée :

```bash
pytest --cov=catalog_api --cov=playlist_api --cov-report=term-missing -v
```

Les lignes non couvertes sont listées avec le préfixe `MISSED`.

---

## 🏗️ Architecture

### Applications Django

1. **catalog_api** : Gestion du catalogue musical (artistes, albums, chansons)
   - API REST avec Django REST Framework
   - Authentification JWT
   - Filtrage et recherche
   - Rate limiting

2. **playlist_api** : Gestion des playlists
   - API GraphQL avec Graphene
   - Mutations pour les opérations d'écriture
   - Authentification requise

3. **web_interface** : Interface web
   - Templates Django
   - Vue de gestion manuelle des données

### Endpoints principaux

#### REST API - Catalog

- `GET/POST /api/catalog/artists/` - Artistes
- `GET/POST /api/catalog/albums/` - Albums
- `GET/POST /api/catalog/songs/` - Chansons
- `POST /api/token/` - Obtenir un JWT

#### GraphQL

- `POST /graphql/` - Requêtes GraphQL (authentification requise)

#### Documentation

- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc
- `GET /api/schema/` - Schéma OpenAPI

### Authentification et Autorisations

- **JWT** : Via `djangorestframework-simplejwt`
- **Permissions personnalisées** :
  - `IsAuthenticatedReadOnly` : Lecture seule pour les authentifiés
  - `IsContributorOrReadOnly` : Écriture pour les contributeurs/admins

### Rate Limiting

- **Anonymes** : 100 requêtes/minute
- **Authentifiés** : 1000 requêtes/minute
- **GraphQL Mutation** : Plus strict pour les écritures

---

## 📚 Ressources supplémentaires

- [Django Documentation](https://docs.djangoproject.com/en/5.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Graphene Django](https://docs.graphene-python.org/projects/django/en/latest/)
- [pytest Documentation](https://docs.pytest.org/)

---


