from datetime import datetime


def get_current_date() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M")
