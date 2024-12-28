from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Student
from school.models import Classe

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Prénom')
    last_name = forms.CharField(max_length=30, required=True, label='Nom')
    email = forms.EmailField(max_length=254, required=True, label='Email')
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        required=True,
        label='Classe'
    )
    photo = forms.ImageField(required=False, label='Photo')
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='Biographie'
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'classe',
            'photo',
            'bio'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            student = Student.objects.create(
                user=user,
                classe=self.cleaned_data['classe'],
                photo=self.cleaned_data.get('photo'),
                bio=self.cleaned_data.get('bio', 'Votre bio')
            )
        return user

class BulkStudentUploadForm(forms.Form):
    file = forms.FileField(
        label='Fichier Excel',
        help_text='Téléchargez un fichier Excel contenant la liste des étudiants. '
                 'Le fichier doit contenir les colonnes : Nom, Prénom, Email, Classe'
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        required=True,
        label='Classe par défaut',
        help_text='Cette classe sera utilisée si aucune classe n\'est spécifiée dans le fichier'
    )
