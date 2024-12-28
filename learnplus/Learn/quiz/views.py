from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .models import Quiz, Question, Answer, QuizAttempt, StudentResponse, Assignment, AssignmentSubmission
from .forms import (
    QuizForm, QuestionForm, AnswerForm, QuizAttemptForm,
    StudentResponseForm, AssignmentForm, AssignmentSubmissionForm
)

@login_required
def liste_quiz(request, cours_id):
    """Liste tous les quiz disponibles pour un cours"""
    quizzes = Quiz.objects.filter(cours_id=cours_id, status=True)
    for quiz in quizzes:
        quiz.can_attempt = quiz.can_student_attempt(request.user)
        quiz.user_attempts = quiz.get_student_attempts(request.user)
    
    context = {
        'quiz_list': quizzes,
    }
    return render(request, 'quiz/liste_quiz.html', context)

@login_required
def detail_quiz(request, quiz_id):
    """Affiche les détails d'un quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, status=True)
    if not quiz.is_available():
        messages.error(request, "Ce quiz n'est pas disponible actuellement.")
        return redirect('quiz:liste_quiz', cours_id=quiz.cours.id)
    
    context = {
        'quiz': quiz,
        'can_attempt': quiz.can_student_attempt(request.user),
        'previous_attempts': quiz.attempts.filter(student=request.user).order_by('-started_at'),
    }
    return render(request, 'quiz/detail_quiz.html', context)

@login_required
def start_quiz(request, quiz_id):
    """Démarre une nouvelle tentative de quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, status=True)
    if not quiz.can_student_attempt(request.user):
        messages.error(request, "Vous ne pouvez plus tenter ce quiz.")
        return redirect('quiz:detail_quiz', quiz_id=quiz.id)
    
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        student=request.user
    )
    return redirect('quiz:quiz_question', attempt_id=attempt.id)

@login_required
def quiz_question(request, attempt_id):
    """Affiche et traite une question de quiz"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    if attempt.is_completed:
        return redirect('quiz:quiz_result', attempt_id=attempt.id)
    
    # Trouve la prochaine question non répondue
    answered_questions = attempt.responses.values_list('question_id', flat=True)
    next_question = attempt.quiz.questions.exclude(id__in=answered_questions).first()
    
    if not next_question:
        # Toutes les questions ont été répondues
        attempt.completed_at = timezone.now()
        attempt.calculate_score()
        attempt.save()
        return redirect('quiz:quiz_result', attempt_id=attempt.id)
    
    if request.method == 'POST':
        form = StudentResponseForm(request.POST, question=next_question)
        if form.is_valid():
            response = form.save(commit=False)
            response.attempt = attempt
            response.question = next_question
            response.save()
            form.save_m2m()  # Pour sauvegarder les relations ManyToMany
            response.check_correctness()
            return redirect('quiz:quiz_question', attempt_id=attempt.id)
    else:
        form = StudentResponseForm(question=next_question)
    
    context = {
        'attempt': attempt,
        'question': next_question,
        'form': form,
        'time_left': (attempt.started_at + timezone.timedelta(minutes=attempt.quiz.duree)) - timezone.now(),
    }
    return render(request, 'quiz/question.html', context)

@login_required
def quiz_result(request, attempt_id):
    """Affiche les résultats d'une tentative de quiz"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    if not attempt.is_completed:
        return redirect('quiz:quiz_question', attempt_id=attempt.id)
    
    context = {
        'attempt': attempt,
        'responses': attempt.responses.all().select_related('question'),
    }
    return render(request, 'quiz/result.html', context)

@login_required
def liste_assignments(request, cours_id):
    """Liste tous les devoirs disponibles pour un cours"""
    assignments = Assignment.objects.filter(cours_id=cours_id, status=True)
    for assignment in assignments:
        assignment.user_submission = assignment.submissions.filter(student=request.user).first()
    
    context = {
        'assignments': assignments,
    }
    return render(request, 'quiz/liste_assignments.html', context)

@login_required
def detail_assignment(request, assignment_id):
    """Affiche les détails d'un devoir et gère les soumissions"""
    assignment = get_object_or_404(Assignment, id=assignment_id, status=True)
    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()
    
    if request.method == 'POST':
        if not assignment.is_available():
            messages.error(request, "La date limite de soumission est dépassée.")
            return redirect('quiz:detail_assignment', assignment_id=assignment.id)
        
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, "Votre devoir a été soumis avec succès.")
            return redirect('quiz:detail_assignment', assignment_id=assignment.id)
    else:
        form = AssignmentSubmissionForm(instance=submission)
    
    context = {
        'assignment': assignment,
        'submission': submission,
        'form': form,
    }
    return render(request, 'quiz/detail_assignment.html', context)

# API Views pour les requêtes AJAX
@login_required
def check_time_remaining(request, attempt_id):
    """Vérifie le temps restant pour une tentative de quiz"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    if attempt.is_completed:
        return JsonResponse({'completed': True})
    
    end_time = attempt.started_at + timezone.timedelta(minutes=attempt.quiz.duree)
    time_left = (end_time - timezone.now()).total_seconds()
    
    if time_left <= 0:
        attempt.completed_at = timezone.now()
        attempt.calculate_score()
        attempt.save()
        return JsonResponse({'completed': True})
    
    return JsonResponse({
        'completed': False,
        'time_left': time_left
    })
