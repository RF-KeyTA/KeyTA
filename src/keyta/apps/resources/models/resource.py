from django.db import models


class Resource(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Name')
    documentation = models.TextField(verbose_name='Dokumentation')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ressource'
        verbose_name_plural = 'Ressourcen'
