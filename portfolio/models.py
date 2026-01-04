from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Technology(models.Model):
    """Technologies used in projects"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class or emoji')
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_project_count(self):
        """Get count of projects using this technology"""
        return self.projects.filter(is_active=True).count()


class Category(models.Model):
    """Project categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class or emoji')
    color = models.CharField(max_length=7, default='#28a745', help_text='Hex color code')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_project_count(self):
        """Get count of active projects in this category"""
        return self.projects.filter(is_active=True).count()


class Project(models.Model):
    """Portfolio projects"""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('featured', 'Featured'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    detailed_description = models.TextField(blank=True, help_text='Detailed project description')

    # Images and media
    featured_image = models.URLField(blank=True, help_text='URL to featured image')
    image_alt = models.CharField(max_length=200, blank=True)
    gallery_images = models.JSONField(blank=True, null=True, help_text='List of image URLs')

    # Project details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    is_active = models.BooleanField(default=True)

    # Links
    live_url = models.URLField(blank=True, help_text='Live project URL')
    github_url = models.URLField(blank=True, help_text='GitHub repository URL')
    demo_url = models.URLField(blank=True, help_text='Demo video or additional demo URL')

    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    launch_date = models.DateField(null=True, blank=True)

    # Relationships
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects')
    technologies = models.ManyToManyField(Technology, related_name='projects')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    # SEO and meta
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)

    # Ordering
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower = higher priority)')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-launch_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Set meta title if not provided
        if not self.meta_title:
            self.meta_title = self.title[:200]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_duration(self):
        """Get project duration in months"""
        if self.end_date and self.start_date:
            delta = self.end_date - self.start_date
            return max(1, round(delta.days / 30))
        elif self.start_date and not self.end_date:
            # Ongoing project
            from datetime import date
            delta = date.today() - self.start_date
            return max(1, round(delta.days / 30))
        return None

    def get_technologies_list(self):
        """Get technologies as a comma-separated string"""
        return ', '.join([tech.name for tech in self.technologies.all()])

    def get_related_projects(self, limit=3):
        """Get related projects based on category and technologies"""
        related_projects = Project.objects.filter(
            is_active=True,
            category=self.category
        ).exclude(id=self.id)[:limit]

        if related_projects.count() < limit:
            # Also get projects with same technologies
            tech_projects = Project.objects.filter(
                is_active=True,
                technologies__in=self.technologies.all()
            ).exclude(id=self.id).distinct()[:limit - related_projects.count()]

            related_projects = list(related_projects) + list(tech_projects)

        return related_projects[:limit]

    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def get_absolute_url(self):
        """Get the URL for this project"""
        from django.urls import reverse
        return reverse('portfolio:project_detail', kwargs={'slug': self.slug})

    def is_featured(self):
        """Check if project is featured"""
        return self.visibility == 'featured'

    def is_completed(self):
        """Check if project is completed"""
        return self.status == 'completed'


class ProjectImage(models.Model):
    """Additional images for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.project.title}"


class Testimonial(models.Model):
    """Client testimonials for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testimonials')
    client_name = models.CharField(max_length=100)
    client_position = models.CharField(max_length=100, blank=True)
    client_company = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5, help_text='Rating out of 5')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial from {self.client_name} for {self.project.title}"


# Utility functions
def get_featured_projects(limit=6):
    """Get featured projects for homepage"""
    return Project.objects.filter(
        is_active=True,
        visibility__in=['public', 'featured']
    ).order_by('order', '-launch_date')[:limit]


def get_projects_by_category(category_slug, limit=None):
    """Get projects by category slug"""
    projects = Project.objects.filter(
        is_active=True,
        visibility__in=['public', 'featured'],
        category__slug=category_slug
    ).order_by('order', '-launch_date')

    if limit:
        projects = projects[:limit]
    return projects


def get_projects_by_technology(tech_slug, limit=None):
    """Get projects by technology slug"""
    projects = Project.objects.filter(
        is_active=True,
        visibility__in=['public', 'featured'],
        technologies__slug=tech_slug
    ).order_by('order', '-launch_date')

    if limit:
        projects = projects[:limit]
    return projects


def get_completed_projects():
    """Get all completed projects"""
    return Project.objects.filter(
        is_active=True,
        status='completed',
        visibility__in=['public', 'featured']
    ).order_by('order', '-launch_date')
