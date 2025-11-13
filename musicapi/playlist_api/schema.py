import graphene
from .queries import Query as PlaylistQuery
from .mutations import Mutation as PlaylistMutation

class Query(PlaylistQuery, graphene.ObjectType):
    pass

class Mutation(PlaylistMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
