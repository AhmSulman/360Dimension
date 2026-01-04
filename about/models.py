from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    """Skills and technologies"""
    CATEGORY_CHOICES = [
        ('programming', 'Programming Languages'),
        ('framework', 'Frameworks & Libraries'),
        ('database', 'Databases'),
        ('tool', 'Tools & Platforms'),
        ('soft', 'Soft Skills'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    proficiency = models.PositiveIntegerField(default=75, help_text='Proficiency level 1-100')
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class or emoji')
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'category', 'name']

    def __str__(self):
        return self.name

    def get_proficiency_percentage(self):
        """Get proficiency as percentage string"""
        return f"{self.proficiency}%"

    def get_proficiency_level(self):
        """Get proficiency level description"""
        if self.proficiency >= 90:
            return 'Expert'
        elif self.proficiency >= 75:
            return 'Advanced'
        elif self.proficiency >= 60:
            return 'Intermediate'
        elif self.proficiency >= 40:
            return 'Beginner'
        else:
            return 'Learning'


class Experience(models.Model):
    """Work experience"""
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]

    company_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)

    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    # Description
    description = models.TextField()
    achievements = models.JSONField(blank=True, null=True, help_text='List of key achievements')

    # Company details
    company_website = models.URLField(blank=True)
    company_logo = models.URLField(blank=True)

    # Skills used
    skills_used = models.ManyToManyField(Skill, blank=True, related_name='experiences')

    # Ordering
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order', '-start_date']

    def save(self, *args, **kwargs):
        if self.is_current:
            self.end_date = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.position} at {self.company_name}"

    def get_duration(self):
        """Get experience duration in months"""
        if self.end_date and self.start_date:
            delta = self.end_date - self.start_date
            months = delta.days // 30
            years = months // 12
            remaining_months = months % 12

            if years > 0:
                return f"{years} year{'s' if years > 1 else ''} {remaining_months} month{'s' if remaining_months != 1 else ''}"
            else:
                return f"{months} month{'s' if months != 1 else ''}"
        elif self.start_date and self.is_current:
            # Current position
            from datetime import date
            delta = date.today() - self.start_date
            months = delta.days // 30
            years = months // 12
            remaining_months = months % 12

            if years > 0:
                return f"{years} year{'s' if years > 1 else ''} {remaining_months} month{'s' if remaining_months != 1 else ''}"
            else:
                return f"{months} month{'s' if months != 1 else ''}"
        return "Unknown"


class Education(models.Model):
    """Education background"""
    DEGREE_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]

    institution_name = models.CharField(max_length=200)
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)

    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    # Details
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    achievements = models.JSONField(blank=True, null=True, help_text='List of achievements')

    # Institution details
    institution_website = models.URLField(blank=True)
    institution_logo = models.URLField(blank=True)

    # Ordering
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order', '-start_date']
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution_name}"


class TeamMember(models.Model):
    """Team members for about page"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    avatar = models.URLField(blank=True, help_text='Avatar image URL')
    avatar_emoji = models.CharField(max_length=10, blank=True, help_text='Emoji avatar if no image')

    # Contact information
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    website = models.URLField(blank=True)

    # Skills and experience
    skills = models.ManyToManyField(Skill, blank=True, related_name='team_members')
    experiences = models.ManyToManyField(Experience, blank=True, related_name='team_members')

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.role}"

    def get_display_avatar(self):
        """Get avatar for display (image or emoji)"""
        return self.avatar or self.avatar_emoji or '👤'

    def get_social_links(self):
        """Get all social media links"""
        links = {}
        if self.linkedin:
            links['linkedin'] = self.linkedin
        if self.github:
            links['github'] = self.github
        if self.twitter:
            links['twitter'] = self.twitter
        if self.website:
            links['website'] = self.website
        return links


class Certification(models.Model):
    """Professional certifications"""
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)

    # Associated with
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='certifications')

    # Details
    description = models.TextField(blank=True)
    skills_validated = models.ManyToManyField(Skill, blank=True, related_name='certifications')

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.name} by {self.issuing_organization}"

    def is_expired(self):
        """Check if certification is expired"""
        if self.expiry_date:
            from datetime import date
            return date.today() > self.expiry_date
        return False


class Project(models.Model):
    """Personal or side projects"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.ManyToManyField(Skill, blank=True, related_name='projects')
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    image = models.URLField(blank=True)

    # Associated with
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='projects')

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


# Utility functions
def get_featured_team_members():
    """Get featured team members for homepage"""
    return TeamMember.objects.filter(is_active=True, is_featured=True).order_by('order')


def get_all_skills():
    """Get all active skills grouped by category"""
    skills = Skill.objects.filter(is_active=True).order_by('category', 'order', 'name')
    grouped_skills = {}

    for skill in skills:
        if skill.category not in grouped_skills:
            grouped_skills[skill.category] = []
        grouped_skills[skill.category].append(skill)

    return grouped_skills


def get_experience_timeline():
    """Get all experiences in chronological order"""
    return Experience.objects.filter(is_active=True).order_by('-start_date')


def get_education_history():
    """Get education history"""
    return Education.objects.filter(is_active=True).order_by('-start_date')
