from evibes.settings import CONSTANCE_CONFIG

JAZZMIN_SETTINGS = {
    "site_title": f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} DASHBOARD",
    "site_header": f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} DASHBOARD",
    "site_brand": f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]}",
    "site_logo": "logo.png",
    "site_icon": 'favicon.png',
    "welcome_sign": "Whoa! Only admins allowed here!",
    "copyright": f"{CONSTANCE_CONFIG.get('COMPANY_NAME')[0]}",
    "user_avatar": "avatar",
    "theme": "darkly",
    "show_ui_builder": False,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://t.me/fureunoir", "new_window": True},
        {"model": "core.Product"},
        {"model": "auth2.User"},
    ],
    "usermenu_links": [
        {"name": "Support", "url": "https://t.me/fureunoir", "new_window": True},
        {"model": "auth2.User"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "use_google_fonts_cdn": True,
    "language_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}
