from django.db import models

# Create your models here.

class Webpages(models.Model):
    url1 = models.URLField(max_length=2048, null=True, blank=True)
    url2 = models.URLField(max_length=2048, null=True, blank=True)
    url3 = models.URLField(max_length=2048, null=True, blank=True)
    url4 = models.URLField(max_length=2048, null=True, blank=True)
    url5 = models.URLField(max_length=2048, null=True, blank=True)