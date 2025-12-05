**Modélisation API**

Étudiant: LOKOSSOU Geordy Kouassi Benedictus 
Date: 04/12/2025 
Contexte: Plateforme de Freelance

**1. Analyse du Besoin**

--1.1 Résumé du Contexte--

Il s'agit de concevoir une API pour une place de marché (marketplace) mettant en relation des clients (porteurs de projets) et des freelancers. 
Le système doit pouvoir gérer: publication d'offres, soumission de devis, contractualisation, livraison et évaluation mutuelle.

--1.2 Contraintes Identifiées--

Intégrité des transactions: Le passage de "Proposition" à "Contrat" puis au "Paiement" bien claire et définis.

Sécurité des données: Protection des données personnelles et sécurisation des informations financières.

Rôles distincts: Un utilisateur peut être Client, Freelancer ou les deux. Cela nécessite alors une gestion bien précise des permissions.

Temps réel: Notifications nécessaires lors de la réception d'une proposition ou de la validation d'un livrable.



**2. Architecture Proposée**

2.1 Choix

Architecture choisie : ☑ REST | ☐ GraphQL | ☐ SOAP | ☐ Hybride

--2.2 Justification du Choix--

Justification 1: J'ai chpoisi l'architecture REST car, la plateforme de freelance, sera essentiellement consultés par de nombreux freelancers. Avec l'architecture REST, je pourrai mettre en cache les requêtes GET /projects facilement pour réduire la charge serveur.

Justification 2: L'API peut évoluer indépendamment de la partie front-end, ce qui est crucial pour maintenir des applications web et mobiles simultanées.

Justification3: Chaque requête contient toutes les informations nécessaires (via token JWT), ce qui facilite la scalabilité horizontale si la plateforme gagne beaucoup d'utilisateurs.

Justification 4 : Standardisation : REST utilise les verbes HTTP standards (GET, POST, PATCH) qui sont standard.


--2.3 Comparaison REST vs GraphQL vs SOAP pour ce Contexte--

**API REST**

Pertinence pour ce cas: Élevée. Le modèle de données est relationnel et structuré.

Avantages: Simple à implémenter, cache HTTP natif, maturité des outils.

Inconvénients: Risque d'over-fetching (trop de données) ou under-fetching.

Conclusion: Retenu.C'est le meilleur compromis simplicité et efficacité pour gérer des ressources claires comme ici.


**API REST**

Pertinence pour ce cas: Élevée. Le modèle de données est relationnel et structuré.

Avantages: Simple à implémenter, cache HTTP natif, maturité des outils.

Inconvénients: Risque d'over-fetching (trop de données) ou under-fetching.

Conclusion: Retenu.C'est le meilleur compromis simplicité et efficacité pour gérer des ressources claires comme ici.

**API GraphQL**

Pertinence pour ce cas: Moyenne. L'API GraphQL serait très utile si le front-end a besoin d'afficher des données complexe.

Avantages: Elle récupère juste ce qu'il faut avec un typage fort.

Inconvénients: Des difficultés de gestion des droits d'accès et pour la mise en cache aussi.

Conclusion: Non retenu pour simplifier l'infrastructure initiale, mais envisageable.

**API SOAP**

Pertinence pour ce cas:  Faible, Elle est trop lourde et verbeux pour une application grand public moderne.

Avantages: Sécurité et transactions ACID distribuées.

Inconvénients: Elle est tres lente avec le format XML lourd, parsing lent.

Conclusion: Non retenu car inadapté pour cette applications web moderne.

**3. Modélisation des Données**

3.1 Diagramme Entité-Relation

┌────────────────┐          ┌────────────────┐          ┌────────────────┐
│      User      │ 1      N │    Project     │ 1      N │    Proposal    │
├────────────────┤◄─────────┤ (Client)       ├─────────►│                │
│ id (PK)        │          │ id (PK)        │          │ id (PK)        │
│ type           │          │ status         │          │ bid_amount     │
└───────┬────────┘          └────────┬───────┘          └───────┬────────┘
        │                            │ 1                        │
        │                            ▼ 1                        │ N
        │                   ┌────────────────┐                  │
        │ 1               N │    Contract    │◄─────────────────┘
        └──────────────────►│                │
          (Freelancer)      │ id (PK)        │
                            │ status         │
                            └────────┬───────┘
                                     │ 1
                                     ▼ N
                            ┌────────────────┐
                            │     Review     │
                            │                │
                            └────────────────┘

### 3.2 Entités Principales

#### Entité 1 : User

id(Integer, PK): Identifiant unique

email(String): Email de connexion (Unique)

full_name(String): Nom 

type (String): Rôle principal ('CLIENT', 'FREELANCER', 'ADMIN')

created_at (DateTime): Date d'inscription

Relations:

1:N avec Project (en tant que Client)
1:N avec Proposal (en tant que Freelancer)
1:N avec Review (en tant qu'auteur)

Champs calculés:

rating (Double):

Description: Note moyenne de l'utilisateur.

Méthode de calcul: Moyenne des colonnes rating de la table Review où l'utilisateur est la cible du contrat.

### Entité 2 : Project

id (Integer, PK): Identifiant unique

title (String): Nom du projet

description (Text): Cahier des charges

budget (Double): Budget estimé

deadline (DateTime): Date limite de réalisation pour livraison

status (String) : État ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')

Relations :

N:1 avec User (via client_id)
1:N avec Proposal
1:1 avec Contract (généralement un projet aboutit à un contrat principal)


### Entité 3 : Proposal

id (Integer, PK): Identifiant unique

bid_amount (Double): Prix proposé par le freelancer

proposal_text (Text) : Lettre de motivation/Compétences proposé par le freelancer

status (String) : État ('PENDING', 'ACCEPTED', 'REJECTED')

Relations :

N:1 avec Project (via project_id)
N:1 avec User (via freelancer_id)

### Entité 4 : Contract

id(Integer, PK): Identifiant unique

amount (Double): Montant final de la prestation

status (String): État du contrat ('ACTIVE', 'DELIVERED', 'PAID', 'DISPUTED')

completed_at (DateTime): Date de fin réelle

Relations:

N:1 avec Project (via project_id)
N:1 avec User (via freelancer_id)
1:N avec Review

### 4. API REST

4.1 Configuration de Base

Base URL : https://api.freelance-market.com/v1

Format : JSON

4.2 Endpoints Principaux
Endpoint 1 : Liste des projets
Method   : GET
Path     : /projects
Descrip. : Récupérer la liste des projets ouverts (pour les freelancers).

Params   :
  - page (optional, Integer) : Pagination (default: 1)
  - min_budget (optional, Double) : Filtrer par budget minimum
  - search (optional, String) : Recherche textuelle dans le titre/description

Response (200 OK):
{
  "count": 42,
  "data": [
    {
      "id": 101,
      "title": "Création site E-commerce",
      "budget": 1000,
      "client": { "id": 5, "name": "Jean Dupont", "rating": 4.8 },
      "created_at": "2023-10-27T10:00:00Z"
    }
  ]
}

Errors:
  - 400 Bad Request : Format de paramètre invalide
  - 500 Internal Server Error

Endpoint 2 : Soumettre une proposition

Method   : POST
Path     : /projects/{id}/proposals
Descrip. : Un freelancer soumet une proposition pour un projet spécifique.

Body     :
{
  "bid_amount": 1400.0,
  "proposal_text": "Bonjour, je suis ingénieur IA..."
}

Response (201 Created):
{
  "id": 55,
  "status": "PENDING",
  "project_id": 101,
  "created_at": "2025-12-28T09:00:00Z"
}

Errors:
  - 401 Unauthorized : Token manquant
  - 403 Forbidden : Seul un profil 'FREELANCER' peut répondre
  - 404 Not Found : Projet introuvable ou fermé
  - 422 Unprocessable Entity : Budget négatif ou texte vide

Endpoint 3 : Finaliser un contrat (Payer/Clôturer)

Method   : PATCH
Path     : /contracts/{id}
Descrip. : Le client valide la livraison et change le statut du contrat pour le paiement.

Body     :
{
  "status": "PAID"
}

Response (200 OK):
{
  "id": 302,
  "status": "PAID",
  "completed_at": "2023-11-15T14:30:00Z"
}

Errors:
  - 401 Unauthorized : Non connecté
  - 403 Forbidden : Seul le client propriétaire du contrat peut valider
  - 409 Conflict : Le contrat n'est pas dans un état permettant la clôture

### 6. Sécurité et Authentification

6.1 Mécanisme d'Authentification

Choix : JWT (JSON Web Token)

Justification: Le JWT est "stateless". Le serveur n'a pas besoin de stocker la session en mémoire, ce qui est idéal pour une marketplace qui doit pouvoir monter en charge (scalabilité). De plus, le JWT peut contenir le rôle de l'utilisateur (type: client ou freelancer) directement dans son payload, évitant des requêtes BDD inutiles pour vérifier les droits simples.

### 6.2 Système d'Autorisation

Modèle: Role-Based Access Control

Rôles définis:

ADMIN: Peut supprimer n'importe quel contenu illégal ou modérer les litiges.
GUEST: Peut voir les projets (GET /projects) mais ne peut pas interagir.
FREELANCER: Peut créer des Proposals, voir ses Contracts.
CLIENT: Peut créer des Projects, accepter des Proposals, valider des Contracts.

### 6.3 Protection des Données Sensibles

Chiffrement: Toutes les communications passent par HTTPS pour éviter l'interception des devis ou données bancaires.

Mots de passe: Hachés avec Argon2 avant stockage.

Données bancaires: Non stockées localement ; utilisation d'un tiers de paiement (ex: Stripe) via tokenisation.

### 6.4 Validation des Entrées

Utilisation dU schéma de validation stricts DRF Serializers pour rejeter tout champ inattendu.

Vérification que budget et bid_amount sont positifs.

Sanitization des champs textes (description, proposal_text) pour empêcher les attaques.

### 6.5 Autres éléments de sécurité

Rate Limiting : Limiter le nombre de propositions qu'un freelancer peut envoyer par heure/jour pour éviter le spam.
CORS : Configuration stricte pour n'autoriser que le domaine du front-end à interroger l'API.


### 8.1 Conclusion

Pour ce projet, j'ai choisi une architecture REST car elle est simple et efficace pour gérer les différentes étapes, de la création d'un projet jusqu'au paiement. J'ai défini 5 modèles de données principaux (User, Project, Proposal, Contract, Review) qui permettent de couvrir tous les besoins de la plateforme.

Côté sécurité, j'ai opté pour des tokens JWT et une gestion des rôles (RBAC), ce qui est idéal pour séparer clairement les actions des clients et des freelancers. L'API est prête à être connectée à une application web ou mobile. Pour aller plus loin, on pourrait par la suite ajouter un système de chat en

### 8.2 Statistiques

Nombre de modèles : 5 
Nombre d'endpoints principaux décrits : 3 
Nombre de rôles gérés : 4