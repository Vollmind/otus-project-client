from client_app.models import Settings


def save_setting(name, value):
    setting, created = Settings.objects.get_or_create(name=name)
    setting.value = value
    setting.save()


def get_setting(name):
    try:
        return Settings.objects.get(name=name).value
    except Settings.DoesNotExist:
        return None
