from django.db import models
from accounts.models import CustomUser
from papers.models import Paper
import uuid
import base58
from django.utils.timezone import now
# Create your models here.

class Project(models.Model):
    class Meta:
        db_table = "project"
    
    project_id = models.UUIDField(verbose_name="project id", default=uuid.uuid4, editable=False, primary_key=True)
    short_project_id = models.CharField(verbose_name="project_id", max_length=8, editable=False, unique=True)
    name = models.TextField(verbose_name="name")
    members = models.ManyToManyField(CustomUser, verbose_name="member", related_name="projects")
    description = models.TextField(verbose_name="description", blank=True, null=True)
    project_url = models.URLField(verbose_name="project URL", max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="作成日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True)
    is_public = models.BooleanField(verbose_name="is_public", default=False)
    is_visible = models.BooleanField(verbose_name="is_visible", default=True)
    bookmark_user = models.ManyToManyField(CustomUser, verbose_name="bookmark_user", related_name="bookmark_project")

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.short_project_id:
            self.short_project_id = base58.b58encode(self.project_id.bytes).decode('utf-8')[:8]
        
        super().save(*args, **kwargs)


class PapersIndices(models.Model):
    class Meta:
        db_table = "papers_indices"
        constraints = [
            models.UniqueConstraint(fields=['index', 'project'], name='unique_index_project'),
            models.UniqueConstraint(fields=['paper', 'project'], name='unique_paper_project')
        ]
    
    index = models.IntegerField(verbose_name="index")
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    description = models.TextField(verbose_name="description", blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="papers_indices")

    def __str__(self):
        return self.project.name + self.paper.title

    def save(self, *args, **kwargs):
        # 親モデルのupdated_atを更新
        if self.project:
            self.project.updated_at = now()
            self.project.save()

        # 子モデル自体の保存
        super().save(*args, **kwargs)
        

class Post(models.Model):
    class Meta:
        db_table = "post"
    
    contributer = models.ForeignKey(CustomUser, verbose_name="contributer", on_delete=models.PROTECT)
    project = models.ForeignKey(Project, verbose_name="project", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(verbose_name="content")
    posted_on = models.DateTimeField(verbose_name="posted_on", auto_now_add=True)

    def __str__(self):
        return self.content[:20]
    
    def save(self, *args, **kwargs):
        # 親モデルのupdated_atを更新
        if self.project:
            self.project.updated_at = now()
            self.project.save()

        # 子モデル自体の保存
        super().save(*args, **kwargs)