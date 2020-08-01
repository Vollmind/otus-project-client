from django.forms import ModelForm, CharField, GenericIPAddressField, PasswordInput, Form

from client_app.models import Storage


class StorageForm(ModelForm):
    class Meta:
        model = Storage
        fields = ['path']


class LoginForm(Form):
    server = GenericIPAddressField()
    login = CharField()
    password = CharField(widget=PasswordInput)
