from django.shortcuts import render, get_object_or_404
from .models import (
    TeamMember, Skill, Experience, Education, Certification,
    get_featured_team_members, get_all_skills, get_experience_timeline, get_education_history
)


def index(request):
    """About page"""
    # Get featured team members
    team_members = get_featured_team_members()

    # If no team members in database, show default data
    if not team_members.exists():
        team_members = [
            {
                'name': 'Ahmed',
                'role': 'Full Stack Developer',
                'bio': 'Passionate about creating amazing digital experiences',
                'avatar': '👨‍💻'
            },
            {
                'name': 'Sarah',
                'role': 'UI/UX Designer',
                'bio': 'Crafting beautiful and intuitive user interfaces',
                'avatar': '👩‍🎨'
            },
            {
                'name': 'Mike',
                'role': 'DevOps Engineer',
                'bio': 'Ensuring smooth deployment and scalability',
                'avatar': '👨‍🔧'
            }
        ]
    else:
        # Convert model instances to dict format for template compatibility
        team_members = [{
            'name': member.name,
            'role': member.role,
            'bio': member.bio,
            'avatar': member.get_display_avatar(),
        } for member in team_members]

    # Get skills grouped by category
    skills_by_category = get_all_skills()

    # Get experience timeline
    experiences = get_experience_timeline()

    # Get education history
    education = get_education_history()

    context = {
        'team': team_members,
        'skills_by_category': skills_by_category,
        'experiences': experiences,
        'education': education,
    }

    return render(request, 'about/index.html', context)


def team_member_detail(request, pk):
    """Individual team member detail page"""
    team_member = get_object_or_404(TeamMember, pk=pk, is_active=True)

    # Get related data
    skills = team_member.skills.filter(is_active=True)
    experiences = team_member.experiences.filter(is_active=True)
    certifications = team_member.certifications.filter(is_active=True)
    projects = team_member.projects.filter(is_active=True)

    context = {
        'member': team_member,
        'skills': skills,
        'experiences': experiences,
        'certifications': certifications,
        'projects': projects,
    }

    return render(request, 'about/member_detail.html', context)


def skills(request):
    """Skills page - detailed view of all skills"""
    skills_by_category = get_all_skills()

    context = {
        'skills_by_category': skills_by_category,
    }

    return render(request, 'about/skills.html', context)


def experience(request):
    """Experience timeline page"""
    experiences = get_experience_timeline()

    context = {
        'experiences': experiences,
    }

    return render(request, 'about/experience.html', context)
