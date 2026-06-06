from django.contrib import admin
from .models import Questions, Badge, StandardBadge, UserProgress, UserScore, UserBadge, UserStandardBadge

@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('text', 'difficulty', 'time_limit_seconds', 'correct_option')
    list_filter = ('difficulty',)
    search_fields = ('text',)
    fieldsets = (
        ('Question', {
            'fields': ('text', 'difficulty', 'time_limit_seconds', 'image', 'explanation')
        }),
        ('Options', {
            'fields': ('option1', 'option2', 'option3', 'option4', 'correct_option')
        }),
    )

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'score_threshold')
    search_fields = ('name',)
    
@admin.register(StandardBadge)
class StandardBadgeAdmin(admin.ModelAdmin):
    list_display = ('level', 'badge_name')
    list_editable = ('badge_name',)
    list_display_links = ('level',)

@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score', 'current_difficulty', 'completed_easy', 'completed_medium', 'completed_hard')
    search_fields = ('user__username',)
    
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    
@admin.register(UserStandardBadge)
class UserStandardBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'standard_badge', 'earned_at')
