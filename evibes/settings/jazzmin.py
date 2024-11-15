from evibes.settings import CONSTANCE_CONFIG

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} Dashboard",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Dashboard",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]}",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "logo.png",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "logo.png",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": "logo.png",

    # CSS classes that are applied to the logo above
    "site_logo_classes": None,

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": "favicon.png",

    # Welcome text on the login screen
    "welcome_sign": "Oops! Only admins allowed here!",

    # Copyright on the footer
    "copyright": f"{CONSTANCE_CONFIG.get('COMPANY_NAME')[0]}",

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": 'avatar',

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://t.me/fureunoir", "new_window": True},

        {"name": "Self GraphQL", "url": f"https://api.{CONSTANCE_CONFIG.get('BASE_DOMAIN')[0]}/graphql", "new_window": True},

        {"name": "Self Swagger", "url": f"https://api.{CONSTANCE_CONFIG.get('BASE_DOMAIN')[0]}/docs/swagger", "new_window": True},

        {"name": "B2B GraphQL", "url": f"https://b2b.{CONSTANCE_CONFIG.get('BASE_DOMAIN')[0]}/graphql", "new_window": True},

        {"name": "B2B Swagger", "url": f"https://b2b.{CONSTANCE_CONFIG.get('BASE_DOMAIN')[0]}/docs/swagger", "new_window": True},

    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": ['django_celery_beat', 'rest_framework_simplejwt.token_blacklist', ],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,

    #############
    # UI Tweaks #
    #############
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
}
