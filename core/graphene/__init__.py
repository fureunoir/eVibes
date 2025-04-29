from graphene import Mutation


class BaseMutation(Mutation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def mutate(**kwargs):
        pass
