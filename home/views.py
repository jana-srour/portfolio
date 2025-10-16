from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
import time
import requests
from bs4 import BeautifulSoup
from .models import App, Experience, Education, SkillCategory, Skill, PersonalSkills
from .models import Project, ProjectStage, Learning, LearningStage, Language
from .forms import ContactForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import AppPrivacyPolicy, AdPublisherID


# Simple in-process cache
_repos_cache = {
    'timestamp': 0,
    'data': [],
}

# Play store cache
_play_cache = {'timestamp': 0, 'data': []}


def privacy_policy(request, app_name):
    policy = get_object_or_404(AppPrivacyPolicy, app_name=app_name)
    return render(request, 'home/policies/privacy_template.html', {'policy': policy})


def ads_txt(request):
    """
    Serve ads.txt dynamically from the database for all apps.
    """
    lines = []
    for ad in AdPublisherID.objects.all():
        # Replace publisher_id and domain if needed
        lines.append(f"google.com, {ad.publisher_id}, DIRECT, f08c47fec0942fa0")
    return HttpResponse("\n".join(lines), content_type="text/plain")

def fetch_github_repos(username):
    if not username:
        return []
    url = f'https://api.github.com/users/{username}/repos'
    headers = {}
    token = getattr(settings, 'GITHUB_TOKEN', None)
    if token:
        headers['Authorization'] = f'token {token}'
    resp = requests.get(url, params={'per_page': 50, 'sort': 'updated'}, headers=headers)
    if resp.status_code != 200:
        return []
    data = resp.json()
    # Map to simple structure - only public repos
    public_repos = [
        {
            'name': r.get('name'),
            'html_url': r.get('html_url'),
            'description': r.get('description') or '',
            'language': r.get('language'),
            'stars': r.get('stargazers_count', 0),
        }
        for r in data
        if not r.get('private')  # filter out private repos
    ]
    return public_repos


def index(request):
    """Homepage view that includes GitHub repos if configured."""
    username = getattr(settings, 'GITHUB_USERNAME', '')
    cache_seconds = getattr(settings, 'GITHUB_CACHE_SECONDS', 300)
    now = time.time()
    if username:
        if now - _repos_cache['timestamp'] > cache_seconds:
            try:
                repos = fetch_github_repos(username)
            except Exception:
                repos = []
            _repos_cache['data'] = repos
            _repos_cache['timestamp'] = now
        else:
            repos = _repos_cache['data']
    else:
        repos = []

    # Play Store apps stored in DB (Admin-managed)
    play_cache_seconds = getattr(settings, 'PLAYSTORE_CACHE_SECONDS', 3600)
    play_apps = []
    now = time.time()
    apps_qs = App.objects.filter(published=True).order_by('-last_synced')
    # If not synced yet, sync them now
    apps_to_sync = [a for a in apps_qs if not a.last_synced or (now - a.last_synced.timestamp() > play_cache_seconds)]
    for a in apps_to_sync:
        try:
            a.sync(fetch_play_store_app)
        except Exception:
            continue
    # Build play_apps list from DB
    play_apps = [
        {
            'package': a.package,
            'title': a.title,
            'developer': a.developer,
            'url': a.playstore_url or f'https://play.google.com/store/apps/details?id={a.package}',
            'icon': a.icon_url,
        }
        for a in apps_qs
    ]

    # Contact form handling
    contact_form = ContactForm()
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            cd = contact_form.cleaned_data
            subject = cd.get('subject') or f'Portfolio contact from {cd.get("name")}'
            body = f"Name: {cd.get('name')}\nEmail: {cd.get('email')}\n\nMessage:\n{cd.get('message')}"

            # Persist submission to DB (re-enable admin visibility)
            from .models import ContactSubmission
            ContactSubmission.objects.create(
                name=cd.get('name'),
                email=cd.get('email'),
                subject=cd.get('subject') or '',
                message=cd.get('message'),
            )
            messages.success(request, 'Thanks — your message was received. I will get back to you soon.')
            return redirect(reverse('home:index') + '#contact')
    
    experiences = Experience.objects.all().order_by('-start_date')
    educations = Education.objects.all().order_by('-start_date')
    skill_categories = SkillCategory.objects.prefetch_related('skills').all()
    projects = Project.objects.prefetch_related('stages').all()
    learnings = Learning.objects.prefetch_related('stages').all()
    languages = Language.objects.all().order_by('-proficiency')
    personal_skills = PersonalSkills.objects.all()

    context = {
        'repos': repos,
        'github_username': username,
        'play_apps': play_apps,
        'contact_form': contact_form,
        'experiences': experiences,
        'educations': educations,
        'skill_categories': skill_categories,
        'projects': projects,
        'learnings': learnings,
        'languages': languages,
        'personal_skills': personal_skills,
    }
    return render(request, 'home/index.html', context)


# Submissions are stored in the ContactSubmission model and are viewable via
# the Django admin. We intentionally do not expose an in-site submissions
# list/detail page to the public.


def fetch_play_store_app(package_name):
    """Scrape basic Play Store details for a package (title, developer, url, icon).
    Note: scraping may break if Play Store markup changes. For production consider using a maintained API."""
    url = f'https://play.google.com/store/apps/details'
    resp = requests.get(url, params={'id': package_name, 'hl': 'en', 'gl': 'US'}, headers={'User-Agent': 'Mozilla/5.0'})
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Title
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else package_name
    # Developer
    dev = 'Novera Labs'
    dev_tag = soup.select_one('[itemprop="author"], a.hrTbp.R8zArc')
    if dev_tag:
        dev = dev_tag.text.strip()
    # Icon
    icon_tag = soup.select_one('img[alt][src]')
    icon = icon_tag['src'] if icon_tag and icon_tag.get('src') else ''
    return {
        'package': package_name,
        'title': title,
        'developer': dev,
        'url': f'https://play.google.com/store/apps/details?id={package_name}',
        'icon': icon,
    }
