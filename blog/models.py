from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    """Blog post categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
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

    def get_post_count(self):
        """Get count of published posts in this category"""
        return self.posts.filter(is_published=True).count()


class Tag(models.Model):
    """Blog post tags"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color code')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_post_count(self):
        """Get count of published posts with this tag"""
        return self.posts.filter(is_published=True).count()


class Post(models.Model):
    """Blog posts"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True, help_text='Short description for previews')
    content = models.TextField()
    featured_image = models.URLField(blank=True, help_text='URL to featured image')
    image_alt = models.CharField(max_length=200, blank=True)

    # Author and status
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    # SEO and meta
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True, help_text='Comma-separated keywords')

    # Relationships
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Set published_at when status changes to published
        if self.status == 'published' and not self.is_published:
            self.is_published = True
            if not self.published_at:
                from django.utils import timezone
                self.published_at = timezone.now()
        elif self.status != 'published':
            self.is_published = False

        # Set meta title if not provided
        if not self.meta_title:
            self.meta_title = self.title[:200]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_reading_time(self):
        """Estimate reading time in minutes"""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))

    def get_related_posts(self, limit=3):
        """Get related posts based on tags and category"""
        related_posts = Post.objects.filter(
            is_published=True,
            category=self.category
        ).exclude(id=self.id)[:limit]

        if related_posts.count() < limit:
            # Also get posts with same tags
            tag_posts = Post.objects.filter(
                is_published=True,
                tags__in=self.tags.all()
            ).exclude(id=self.id).distinct()[:limit - related_posts.count()]

            related_posts = list(related_posts) + list(tag_posts)

        return related_posts[:limit]

    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def get_absolute_url(self):
        """Get the URL for this post"""
        from django.urls import reverse
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    """Comments on blog posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"

    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.filter(is_approved=True)


# Utility functions
def get_featured_posts(limit=5):
    """Get featured posts for homepage"""
    return Post.objects.filter(
        is_published=True,
        status='published'
    ).order_by('-published_at')[:limit]


def get_posts_by_category(category_slug, limit=None):
    """Get posts by category slug"""
    posts = Post.objects.filter(
        is_published=True,
        status='published',
        category__slug=category_slug
    ).order_by('-published_at')

    if limit:
        posts = posts[:limit]
    return posts


def get_posts_by_tag(tag_slug, limit=None):
    """Get posts by tag slug"""
    posts = Post.objects.filter(
        is_published=True,
        status='published',
        tags__slug=tag_slug
    ).order_by('-published_at')

    if limit:
        posts = posts[:limit]
    return posts
