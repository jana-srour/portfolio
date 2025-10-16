from django.contrib import admin
from .models import App
from .views import fetch_play_store_app
from .models import ContactSubmission
from .models import Experience, Education, SkillCategory, Skill, PersonalSkills
from .models import Project, ProjectStage, Learning, LearningStage, Language
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import AppPrivacyPolicy, PolicyPoint, AdPublisherID


@admin.action(description='Sync selected apps from Play Store')
def sync_apps(modeladmin, request, queryset):
	for app in queryset:
		app.sync(fetch_play_store_app)


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
	list_display = ('title', 'package', 'developer', 'published', 'last_synced')
	list_filter = ('published',)
	search_fields = ('title', 'package', 'developer')
	actions = [sync_apps]


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'subject', 'created_at')
	list_filter = ('created_at',)
	search_fields = ('name', 'email', 'subject', 'message')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'major_institution', 'notes', 'start_date_display', 'end_date_display')
    search_fields = ('degree', 'major_institution')

    def start_date_display(self, obj):
        return obj.start_date.strftime("%b %Y") if obj.start_date else "Unknown"
    start_date_display.short_description = "Start Date"

    def end_date_display(self, obj):
        return obj.end_date.strftime("%b %Y") if obj.end_date else "Present"
    end_date_display.short_description = "End Date"


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'start_date_display', 'end_date_display', 'description')
    search_fields = ('title', 'company')

    def start_date_display(self, obj):
        return obj.start_date.strftime("%b %Y") if obj.start_date else "Unknown"
    start_date_display.short_description = "Start Date"

    def end_date_display(self, obj):
        return obj.end_date.strftime("%b %Y") if obj.end_date else "Present"
    end_date_display.short_description = "End Date"


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


class ProjectStageInline(admin.TabularInline):
    model = ProjectStage
    extra = 1


class LearningStageInline(admin.TabularInline):
    model = LearningStage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ProjectStageInline]


@admin.register(Learning)
class LearningAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [LearningStageInline]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'proficiency', 'note')
    search_fields = ('name',)


@admin.register(PersonalSkills)
class PersonalSkillsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



class PolicyPointInline(admin.TabularInline):
    model = PolicyPoint
    extra = 1


@admin.register(AppPrivacyPolicy)
class AppPrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'last_updated')
    inlines = [PolicyPointInline]


@admin.register(AdPublisherID)
class AdPublisherIDAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'publisher_id')
    search_fields = ('app_name', 'publisher_id')
