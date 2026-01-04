from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import (
    Project, Category, Technology,
    get_featured_projects, get_projects_by_category, get_projects_by_technology
)


def index(request):
    """Portfolio index page"""
    # Get featured projects
    featured_projects = get_featured_projects(limit=6)

    # Get all active projects with pagination
    projects_list = Project.objects.filter(is_active=True).order_by('order', '-launch_date')
    paginator = Paginator(projects_list, 12)  # 12 projects per page

    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)

    # Get categories and technologies for filtering
    categories = Category.objects.filter(is_active=True).order_by('name')
    technologies = Technology.objects.filter(is_active=True).order_by('name')

    context = {
        'projects': projects,
        'featured_projects': featured_projects,
        'categories': categories,
        'technologies': technologies,
    }

    return render(request, 'portfolio/index.html', context)


def project_detail(request, slug):
    """Individual project detail page"""
    project = get_object_or_404(Project, slug=slug, is_active=True)

    # Increment view count
    project.increment_views()

    # Get related projects
    related_projects = project.get_related_projects()

    # Get testimonials
    testimonials = project.testimonials.filter(is_featured=True)

    # Get all projects for navigation
    all_projects = Project.objects.filter(is_active=True).order_by('order', '-launch_date')

    # Find current project index for navigation
    current_index = None
    prev_project = None
    next_project = None

    for i, proj in enumerate(all_projects):
        if proj.id == project.id:
            current_index = i
            if i > 0:
                prev_project = all_projects[i-1]
            if i < len(all_projects) - 1:
                next_project = all_projects[i+1]
            break

    context = {
        'project': project,
        'related_projects': related_projects,
        'testimonials': testimonials,
        'prev_project': prev_project,
        'next_project': next_project,
    }

    return render(request, 'portfolio/project_detail.html', context)


def category_projects(request, slug):
    """Projects by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    projects = get_projects_by_category(slug)

    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)

    # Sidebar data
    categories = Category.objects.filter(is_active=True).order_by('name')
    technologies = Technology.objects.filter(is_active=True).order_by('name')

    context = {
        'category': category,
        'projects': projects_page,
        'categories': categories,
        'technologies': technologies,
    }

    return render(request, 'portfolio/category.html', context)


def technology_projects(request, slug):
    """Projects by technology"""
    technology = get_object_or_404(Technology, slug=slug, is_active=True)
    projects = get_projects_by_technology(slug)

    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)

    # Sidebar data
    categories = Category.objects.filter(is_active=True).order_by('name')
    technologies = Technology.objects.filter(is_active=True).order_by('name')

    context = {
        'technology': technology,
        'projects': projects_page,
        'categories': categories,
        'technologies': technologies,
    }

    return render(request, 'portfolio/technology.html', context)
