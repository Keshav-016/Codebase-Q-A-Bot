from django.db import models

# Create your models here.
STATUS_CHOICES = [
    'pending',
    'processing',
    'ready',
    'failed'
]
class GitHubIngest(models.Model):
    repo_url = models.URLField()
    status  =   models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
        )
    created_at = models.DateTimeField(auto_now_add=True)
    last_synced_at  = models.DateTimeField(null=True, blank=True)