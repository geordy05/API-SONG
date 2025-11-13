import graphene
from playlist_api.schema import Query as PlaylistQuery
from playlist_api.schema import Mutation as PlaylistMutation

class Query(PlaylistQuery, graphene.ObjectType):
    pass

class Mutation(PlaylistMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
