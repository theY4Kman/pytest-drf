from django.db import models


class KeyValueManager(models.Manager):
    def create_batch(self, **keys):
        return [
            self.create(key=key, value=value)
            for key, value in keys.items()
        ]


class KeyValue(models.Model):
    key = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=32)

    objects = KeyValueManager()
