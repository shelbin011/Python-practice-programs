from django.db import models


# Day 4: User Model
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Day 4: Job Model
class Job(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Day 4: Application Model
class Application(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.job.title}"
