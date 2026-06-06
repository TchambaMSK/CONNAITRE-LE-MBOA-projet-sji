from django.db import models
from django.contrib.auth.models import User

class Questions(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField() # 1, 2, 3, or 4
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    time_limit_seconds = models.IntegerField(default=30) # in seconds
    image = models.ImageField(upload_to='quiz_images/', null=True, blank=True)
    explanation = models.TextField(help_text="please explain why answer is true", blank=True) # Explanation for the correct answer

    def __str__(self): 
        return f"{self.get_difficulty_display()}: {self.text[:50]}"
    
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    score_threshold = models.IntegerField(help_text="The minimum score required to have the badge")
    icon = models.ImageField(upload_to='badges/', blank=True, null=True) #this part will be obviously optional, but it will be nice to have an icon for each badge
    
    def __str__(self):
        return f"{self.name} (greater than or equal to{self.score_threshold} points)"
    
class StandardBadge(models.Model):
    """Badges automatically given for the difficulty levels you pass or like standard badges"""
    LEVEL_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, unique=True)
    badge_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"Level: {self.get_level_display()} - Badge: {self.badge_name}"
    
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(default=0) # the time taken to answer the question in seconds
    
    class Meta:
        unique_together = ('user', 'question') # Ensure a user can only answer a question once

class UserScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    current_question_index = models.IntegerField(default=0) # To track which question the user is currently on
    current_difficulty = models.CharField(max_length=10, choices=Questions.DIFFICULTY_CHOICES, default='easy')#je dois revenir ici # To track the current difficulty level of the user
    completed_easy = models.BooleanField(default=False) # To track if the user has completed the easy level
    completed_medium = models.BooleanField(default=False) # To track if the user has completed the medium level
    completed_hard = models.BooleanField(default=False) # To track if the user completed hard level
    
    
    def __str__(self):
        return f"{self.user.username}: {self.total_score} points, current difficulty level: {self.get_current_difficulty_display()}"
    
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge') # Ensure a user can only earn each badge once
        
class UserStandardBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    standard_badge = models.ForeignKey(StandardBadge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'standard_badge') # Ensure a user can only earn each standard badge once