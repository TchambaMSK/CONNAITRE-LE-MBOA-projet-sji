from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import Questions, UserScore, UserProgress, Badge, UserBadge, StandardBadge, UserStandardBadge
import random
import json

# Create your views here.

# The HOME (MENU) from here
def home(request):
    if not request.user.is_authenticated:
        return redirect('account_select')
    context = {
        'user': request.user,
    }
    return render(request, 'mboaquizapp/home.html', context)
# The end of home (MENU)

# The RULES PAGE from here
def rules(request):
    return render(request, 'mboaquizapp/rules.html')
# The end of RULES PAGE

# The ACCOUNT SELECTION PAGE from here
def account_select(request):
    return render(request, 'mboaquizapp/account_select.html')

def create_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username and not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=None)
            user.set_unusable_password()
            user.save()
            #here we create an empty user score for the user here
            UserScore.objects.create(user=user)
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username already exists or is invalid.')
    return redirect('account_select')

def login_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('home')
        except User.DoesNotExist:
            messages.error(request, 'Username does not exist.')
    return redirect('account_select')  

def logout_account(request):
    logout(request)
    return redirect('account_select')
# The end of ACCOUNT SELECTION PAGE

# The SELECT DIFFICULTY
def select_difficulty(request):
    if not request.user.is_authenticated:
        return redirect('account_select')
    return render(request, 'mboaquizapp/select_difficulty.html')
# The end of SELECT DIFFICULTY  

# The QUIZ PAGE from here (initialize)
def start_quiz(request, difficulty):
    if difficulty not in ['easy', 'medium', 'hard']:
        return redirect('select_difficulty')
    
    # Fetch questions based on difficulty but the order will be random (anctually not random, but not expected still)
    questions = list(Questions.objects.filter(difficulty=difficulty))
    if not questions:
        messages.error(request, 'No questions available for {difficulty} difficulty for now, please select another difficulty.')
        return redirect('select_difficulty')
    
    random.shuffle(questions)
    
    # Store the question IDs in the session for this quiz attempt
    request.session[f'quiz_{difficulty}'] = [q.id for q in questions]
    request.session[f'quiz_index_{difficulty}'] = 0
    request.session[f'quiz_score_{difficulty}'] = 0
    
    #we will also track the overall progress for the badges
    user_score, created = UserScore.objects.get_or_create(user=request.user)
    user_score.current_difficulty = difficulty
    user_score.save()
    
    return redirect('get_question')
# The end of QUIZ PAGE (initialize)

#Here we will get the question and also handle the answer submission
def get_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Who are you bro?'}, status=401)
    
    difficulty = request.user.userscore.current_difficulty
    session_key = f'quiz_{difficulty}'
    index_key = f'quiz_index_{difficulty}'
    
    if session_key not in request.session:
        return redirect('select_difficulty')
    
    question_ids = request.session[session_key]
    current_index = request.session[index_key]
    
    if current_index >= len(question_ids):
        #the quize will be considered completed for this level
        return redirect('level_complete')
    
    question = get_object_or_404(Questions, id=question_ids[current_index])
    
    #we prepare the data for the frontent
    data = {
        'id': question.id,
        'text': question.text,
        'option1': question.option1,
        'option2': question.option2,
        'option3': question.option3,
        'option4': question.option4,
        'time_limit': question.time_limit_seconds,
        'image_url': question.image.url if question.image else None,
        'difficulty': difficulty,
        'current_question': current_index + 1,
        'total_questions': len(question_ids),
    }
    
    #if JSON is expected
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)
    else: 
        return render(request, 'mboaquizapp/question.html', {'question_data': data})
# The end of get question and handle answer submission

# Answer submission and validation
def submit_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Who are you bro?'}, status=401)
    
    if request.method != 'POST':
        return HttpResponse()
    
    try:
        #if JSON from the frontend
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            question_id = data.get('question_id')
            selected_option = data.get('selected_option')
            time_taken = data.get('time_taken', 0)
        else:
            question_id = request.POST.get('question_id')
            selected_option = request.POST.get('selected_option')
            time_taken = request.POST.get('time_taken', 0)
    except:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    
    question = get_object_or_404(Questions, id=question_id)
    is_correct = (selected_option == str(question.correct_option))
    difficulty = request.user.userscore.current_difficulty
    session_key = f'quiz_{difficulty}'
    score_key = f'quiz_score_{difficulty}'
    
    if is_correct:
        #if correct +1 on the score
        request.session[score_key] = request.session.get(score_key, 0) + 1
        #we also update the permanent score in the database for the user
        user_score = request.user.userscore
        user_score.total_score += 1
        user_score.save()
        
        #recording the progress to prevent replaying same question
        UserProgress.objects.get_or_create(
            user=request.user, 
            question=question,
            defaults={'is_correct': is_correct, 'time_taken': time_taken}
        )
        
        #we move to the next question
        index_key = f'quiz_index_{difficulty}'
        request.session[index_key] = request.session.get(index_key, 0) + 1
        
        #we prepare the feedback for the frontend
        response = {
            'is_correct': is_correct,
            'correct_option': question.correct_option,
            'explanation': question.explanation,
            'score': request.session[score_key],
            'next_question': request.session[index_key] < len(request.session[session_key]),
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response)
        else:
        # For non-AJAX, redirect to next question or complete page  
            if response['next_question']:
                return redirect('get_question')
            else:
                return redirect('level_complete')
# The end of answer submission and validation

# The level complete and badge unlocking section
def level_complete(request):
    if not request.user.is_authenticated:
        return redirect('account_select')
    
    difficulty = request.user.userscore.current_difficulty
    session_key = f'quiz_{difficulty}'
    score_key = f'quiz_score_{difficulty}'
    
    if session_key not in request.session:
        return redirect('select_difficulty')
    
    total_questions = len(request.session[session_key])
    user_score = request.session.get(score_key, 0)
    percentage = (user_score / total_questions) * 100 if total_questions else 0
    
    # we have to mark level completed in UserScore model
    user_score_model = request.user.userscore
    if difficulty == 'easy': 
        user_score_model.completed_easy = True 
    elif difficulty == 'medium':
        user_score_model.completed_medium = True
    elif difficulty == 'hard':
        user_score_model.completed_hard = True
    user_score_model.save()
    
    # now standard badge unlocking for this level (if not already unlocked)
    standard_badge = StandardBadge.objects.filter(level=difficulty).first()
    if standard_badge:
        UserStandardBadge.objects.get_or_create(
            user=request.user, 
            standard_badge=standard_badge
        )
        
    #\/ checking for custom badges unlocking based on the performance
    unlocked_badges = []
    for badge in Badge.objects.all():
        if user_score_model.total_score >= badge.score_threshold:
            obj, created = UserBadge.objects.get_or_create(user=request.user, badge=badge)
            if created:
                unlocked_badges.append(badge.name)

    # we clear the session data for this difficulty
    del request.session[session_key]
    del request.session[score_key]
    del request.session[f'quiz_index_{difficulty}']
    
    context = {
        'difficulty': difficulty,
        'user_score': user_score,
        'total_questions': total_questions,
        'percentage': percentage,
        'unlocked_badges': unlocked_badges,
        'total_score': user_score_model.total_score,
    }
    return render(request, 'mboaquizapp/level_complete.html', context)
# The end of level complete and badge unlocking section

#showing the overall progress (score)
def show_score(request):
    if not request.user.is_authenticated:
        return redirect('account_select')
    
    user_score = request.user.userscore
    context = {
        'total_score': user_score.total_score,
        'completed_easy': user_score.completed_easy,
        'completed_medium': user_score.completed_medium,
        'completed_hard': user_score.completed_hard,
    }
    return render(request, 'mboaquizapp/score.html', context)