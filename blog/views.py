from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Category, Tag, get_featured_posts, get_posts_by_category, get_posts_by_tag


def index(request):
    """Blog index page"""
    # Get featured posts
    featured_posts = get_featured_posts(limit=3)

    # Get recent posts with pagination
    posts_list = Post.objects.filter(is_published=True).order_by('-published_at')
    paginator = Paginator(posts_list, 9)  # 9 posts per page

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    # Get categories and tags for sidebar
    categories = Category.objects.filter(is_active=True).order_by('name')
    tags = Tag.objects.filter(is_active=True).order_by('name')

    # Get recent posts for sidebar
    recent_posts = Post.objects.filter(is_published=True).order_by('-published_at')[:5]

    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }

    return render(request, 'blog/index.html', context)


def post_detail(request, slug):
    """Individual blog post page"""
    post = get_object_or_404(Post, slug=slug, is_published=True)

    # Increment view count
    post.increment_views()

    # Get related posts
    related_posts = post.get_related_posts()

    # Get recent posts for sidebar
    recent_posts = Post.objects.filter(is_published=True).exclude(id=post.id).order_by('-published_at')[:5]

    # Get categories and tags
    categories = Category.objects.filter(is_active=True).order_by('name')
    tags = Tag.objects.filter(is_active=True).order_by('name')

    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'tags': tags,
    }

    return render(request, 'blog/post_detail.html', context)


def category_posts(request, slug):
    """Posts by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    posts = get_posts_by_category(slug)

    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    # Sidebar data
    categories = Category.objects.filter(is_active=True).order_by('name')
    tags = Tag.objects.filter(is_active=True).order_by('name')
    recent_posts = Post.objects.filter(is_published=True).order_by('-published_at')[:5]

    context = {
        'category': category,
        'posts': posts_page,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }

    return render(request, 'blog/category.html', context)


def tag_posts(request, slug):
    """Posts by tag"""
    tag = get_object_or_404(Tag, slug=slug, is_active=True)
    posts = get_posts_by_tag(slug)

    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    # Sidebar data
    categories = Category.objects.filter(is_active=True).order_by('name')
    tags = Tag.objects.filter(is_active=True).order_by('name')
    recent_posts = Post.objects.filter(is_published=True).order_by('-published_at')[:5]

    context = {
        'tag': tag,
        'posts': posts_page,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }

    return render(request, 'blog/tag.html', context)
