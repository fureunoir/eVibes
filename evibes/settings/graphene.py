from evibes.settings.base import *  # noqa: F403

GRAPHENE = {
    "MIDDLEWARE": [
        "evibes.middleware.GrapheneLoggingErrorsDebugMiddleware",
        "evibes.middleware.GrapheneJWTAuthorizationMiddleware",
        "evibes.middleware.GrapheneLocaleMiddleware",
    ]
    if DEBUG  # noqa: F405
    else [
        "evibes.middleware.GrapheneJWTAuthorizationMiddleware",
        "evibes.middleware.GrapheneLocaleMiddleware",
    ],
    "CAMELCASE_ERRORS": True,
}
