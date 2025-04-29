CSP_DEFAULT_SRC = ("'self'",)

CSP_FRAME_ANCESTORS = ("'self'",)

CSP_SCRIPT_SRC = (
    "'self'",
    "'nonce'",
    "https://cdn.jsdelivr.net",
    "https://cdnjs.cloudflare.com",
)

CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
)

CSP_IMG_SRC = ("'self'", "data:", "https://cdn.jsdelivr.net")

CSP_CONNECT_SRC = (
    "'self'",
    "https://api.openai.com",
)

CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
)

CSP_OBJECT_SRC = ("'none'",)

CSP_MEDIA_SRC = ("'self'",)

CSP_FORM_ACTION = ("'self'",)

CSP_WORKER_SRC = ("'self'",)

CSP_REPORT_URI = "/csp-violation/"
