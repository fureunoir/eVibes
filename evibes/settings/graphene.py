from evibes.settings.base import *  # noqa: F403

GRAPHENE = {
    "MIDDLEWARE": [
        "evibes.middleware.GrapheneLoggingErrorsDebugMiddleware",
        "evibes.middleware.GrapheneJWTAuthorizationMiddleware",
    ]
    if DEBUG  # noqa: F405
    else [
        "evibes.middleware.GrapheneJWTAuthorizationMiddleware",
    ],
    "CAMELCASE_ERRORS": True,
}
