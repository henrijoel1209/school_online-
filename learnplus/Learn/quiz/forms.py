from django import forms
from django.core.exceptions import ValidationError
from .models import Quiz, Question, Answer, QuizAttempt, StudentResponse, Assignment, AssignmentSubmission

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['titre', 'description', 'duree', 'tentatives_max', 'note_minimale', 'date_debut', 'date_fin']
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_duree(self):
        duree = self.cleaned_data.get('duree')
        if duree is not None and duree <= 0:
            raise ValidationError("La durée doit être positive")
        return duree

    def clean_tentatives_max(self):
        tentatives = self.cleaned_data.get('tentatives_max')
        if tentatives is not None and tentatives <= 0:
            raise ValidationError("Le nombre de tentatives doit être positif")
        return tentatives

    def clean_note_minimale(self):
        note = self.cleaned_data.get('note_minimale')
        if note is not None and note < 0:
            raise ValidationError("La note minimale ne peut pas être négative")
        return note

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        if date_debut and date_fin and date_fin <= date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début")
        return cleaned_data

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_type', 'texte', 'points', 'explanation']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['texte', 'is_correct']

class QuizAttemptForm(forms.ModelForm):
    class Meta:
        model = QuizAttempt
        fields = []  # No fields needed as they are set automatically

class StudentResponseForm(forms.ModelForm):
    class Meta:
        model = StudentResponse
        fields = ['selected_answers', 'text_response']
        widgets = {
            'selected_answers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        if question:
            self.fields['selected_answers'].queryset = question.answers.all()
            if question.question_type == 'single':
                self.fields['selected_answers'].widget = forms.RadioSelect()
            elif question.question_type == 'text':
                self.fields['selected_answers'].widget = forms.HiddenInput()

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['titre', 'description', 'date_debut', 'date_limite', 'points_max', 'fichier_instruction']
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_limite': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['fichier_reponse', 'commentaire']
