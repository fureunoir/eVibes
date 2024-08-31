from evibes.settings.base import *

GRAPHENE = {
    'SCHEMA': 'core.schema.schema',
    'MIDDLEWARE': [
        'evibes.middleware.JWTAuthorizationMiddleware'
    ],
}
