from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rules/', views.rules, name='rules'),
    path('accounts/', views.account_select, name='account_select'),
    path('accounts/create/', views.create_account, name='create_account'),
    path('accounts/login/', views.login_account, name='login_account'),
    path('quiz/select-difficulty/', views.select_difficulty, name='select_difficulty'),
    path('quiz/start/<str:difficulty>/', views.start_quiz, name='start_quiz'),
    path('quiz/question/', views.get_question, name='get_question'),
    path('quiz/submit/', views.submit_answer, name='submit_answer'),
    path('quiz/score/', views.show_score, name='show_score'),
    path('quiz/level-complete/', views.level_complete, name='level_complete'),
    path('logout/', views.logout_account, name='logout'),
]