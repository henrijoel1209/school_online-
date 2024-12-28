from django import forms
from .models import Sujet, Reponse

class SujetForm(forms.ModelForm):
    class Meta:
        model = Sujet
        fields = ['titre', 'question', 'cours']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du sujet'}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Votre question...'}),
            'cours': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cours'].required = False

class ReponseForm(forms.ModelForm):
    class Meta:
        model = Reponse
        fields = ['reponse']
        widgets = {
            'reponse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Votre réponse...'}),
        }
