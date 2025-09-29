from django.db import models
from django.conf import settings

class LessonPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=200)
    grade = models.CharField(max_length=100)
    topic = models.CharField(max_length=200)
    duration = models.PositiveIntegerField()
    content = models.TextField()
    teacher_actions = models.TextField(blank=True)  # new optional field
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} — {self.topic} ({self.created:%Y-%m-%d %H:%M})"
