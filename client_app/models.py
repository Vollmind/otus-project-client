from django.db import models


class Storage(models.Model):
    path = models.CharField(max_length=4000)
    hidden = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


class File(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=4000)
    file_hash = models.CharField(max_length=1000)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    hidden = models.BooleanField(default=False)
    size = models.IntegerField()


class Settings(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
