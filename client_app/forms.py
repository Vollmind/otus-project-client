import os

from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, GenericIPAddressField, PasswordInput, Form

from client_app.models import Storage


class StorageForm(ModelForm):
    def clean_path(self):
        data = self.cleaned_data['path']
        if not os.path.exists(data):
            raise ValidationError('Path does not exists')
        return data

    class Meta:
        model = Storage
        fields = ['path']


class LoginForm(Form):
    server = GenericIPAddressField()
    login = CharField()
    password = CharField(widget=PasswordInput)
