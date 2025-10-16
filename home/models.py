from django.db import models
from django.utils import timezone


class App(models.Model):
	package = models.CharField(max_length=255, unique=True)
	title = models.CharField(max_length=255, blank=True)
	developer = models.CharField(max_length=255, blank=True)
	icon_url = models.URLField(blank=True)
	playstore_url = models.URLField(blank=True)
	published = models.BooleanField(default=True)
	last_synced = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-last_synced', 'title']

	def __str__(self):
		return self.title or self.package

	def sync(self, fetcher):
		"""Use fetcher(package_name) -> dict to update fields and save."""
		data = fetcher(self.package)
		if not data:
			return False
		self.title = data.get('title', self.title)
		self.developer = data.get('developer', self.developer)
		self.icon_url = data.get('icon', self.icon_url)
		self.playstore_url = data.get('url', self.playstore_url) or f'https://play.google.com/store/apps/details?id={self.package}'
		self.last_synced = timezone.now()
		self.save()
		return True


class ContactSubmission(models.Model):
	name = models.CharField(max_length=150)
	email = models.EmailField()
	subject = models.CharField(max_length=200, blank=True)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Contact from {self.name} <{self.email}> on {self.created_at:%Y-%m-%d %H:%M}"


class Education(models.Model):
    degree = models.CharField(max_length=200)
    major_institution = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        start = self.start_date.strftime("%b %Y") if self.start_date else "Unknown"
        end = self.end_date.strftime("%b %Y") if self.end_date else "Present"
        return f"{self.degree} at {self.major_institution} ({start} – {end})"


class Experience(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        start = self.start_date.strftime("%b %Y") if self.start_date else "Unknown"
        end = self.end_date.strftime("%b %Y") if self.end_date else "Present"
        return f"{self.title} at {self.company} ({start} – {end})"
    

class SkillCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Skill categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200)
    status_choices = (
        ('completed', 'Completed'),
        ('current', 'Current'),
        ('upcoming', 'Upcoming'),
    )
    # Each project can have multiple stages
    def __str__(self):
        return self.name

class ProjectStage(models.Model):
    project = models.ForeignKey(Project, related_name='stages', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Project.status_choices, default='upcoming')

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class Learning(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class LearningStage(models.Model):
    learning = models.ForeignKey(Learning, related_name='stages', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Project.status_choices, default='upcoming')

    def __str__(self):
        return f"{self.learning.name} - {self.name}"


class Language(models.Model):
    name = models.CharField(max_length=50)
    proficiency = models.PositiveIntegerField(help_text="Percentage 0-100")
    note = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.proficiency}%)"


class PersonalSkills(models.Model):
	name = models.CharField(max_length=500)

	def __str__(self):
		return f"{self.name}"


class AppPrivacyPolicy(models.Model):
    app_name = models.CharField(max_length=255, unique=True)
    last_updated = models.DateField(auto_now=True)
    intro_text = models.TextField()
    contact_email = models.EmailField(default='novera.labs1@gmail.com')
    footer_note = models.TextField(default='This Privacy Policy applies only to this app.')

    def __str__(self):
        return self.app_name


class PolicyPoint(models.Model):
    policy = models.ForeignKey(AppPrivacyPolicy, related_name='points', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.policy.app_name} - point"


class AdPublisherID(models.Model):
    app_name = models.CharField(max_length=50)
    publisher_id = models.CharField(max_length=50)
