from constance import config


def get_flag_by_language(language):
    return f"https://api.{config.BASE_DOMAIN}/static/flags/{language}.png"
