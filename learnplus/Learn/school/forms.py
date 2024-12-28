from django import forms
from .models import Chapitre, Cours, Matiere
from PIL import Image

class ChapitreForm(forms.ModelForm):
    class Meta:
        model = Chapitre
        fields = [
            'matiere',
            'classe',
            'titre',
            'description',
            'objectifs',
            'prerequis',
            'ordre',
            'image',
            'video',
            'duree_en_heure',
            'date_debut',
            'date_fin',
            'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'objectifs': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Listez les objectifs d\'apprentissage...'}),
            'prerequis': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Listez les prérequis nécessaires...'}),
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'ordre': forms.NumberInput(attrs={'min': 1, 'value': 1}),
        }
        error_messages = {
            'image': {
                'invalid_image': "Le fichier n'est pas une image valide.",
                'missing': "Ce champ est obligatoire.",
                'invalid': "Format d'image non supporté.",
                'empty': "Le fichier image est vide.",
                'max_length': "Le nom du fichier est trop long.",
                'file_too_large': "L'image ne doit pas dépasser 5MB."
            }
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(
                    self.error_messages['image']['file_too_large'],
                    code='file_too_large'
                )
            try:
                # Vérifier que c'est une image valide
                Image.open(image).verify()
            except:
                raise forms.ValidationError(
                    self.error_messages['image']['invalid_image'],
                    code='invalid_image'
                )
        return image

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin and date_fin < date_debut:
            self.add_error('date_fin', "La date de fin doit être postérieure à la date de début")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs
        self.fields['matiere'].widget.attrs.update({'class': 'form-control'})
        self.fields['classe'].widget.attrs.update({'class': 'form-control'})
        self.fields['titre'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['objectifs'].widget.attrs.update({'class': 'form-control'})
        self.fields['prerequis'].widget.attrs.update({'class': 'form-control'})
        self.fields['ordre'].widget.attrs.update({'class': 'form-control', 'min': '1'})
        self.fields['duree_en_heure'].widget.attrs.update({'class': 'form-control', 'min': '0'})
        self.fields['image'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'image/*'
        })
        self.fields['video'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'video/*'
        })

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = [
            'chapitre',
            'titre',
            'description',
            'objectifs',
            'prerequis',
            'duree',
            'ordre',
            'image',
            'video',
            'fichier',
            'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'objectifs': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Listez les objectifs d\'apprentissage...'}),
            'prerequis': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Listez les prérequis nécessaires...'}),
            'ordre': forms.NumberInput(attrs={'min': 1, 'value': 1}),
        }
        error_messages = {
            'image': {
                'invalid_image': "Le fichier n'est pas une image valide.",
                'missing': "Ce champ est obligatoire.",
                'invalid': "Format d'image non supporté.",
                'empty': "Le fichier image est vide.",
                'max_length': "Le nom du fichier est trop long.",
                'file_too_large': "L'image ne doit pas dépasser 5MB."
            },
            'video': {
                'invalid': "Le fichier vidéo n'est pas valide.",
                'missing': "Ce champ est obligatoire.",
                'empty': "Le fichier vidéo est vide.",
                'max_length': "Le nom du fichier est trop long."
            },
            'fichier': {
                'invalid': "Le type de fichier n'est pas supporté.",
                'missing': "Ce champ est obligatoire.",
                'empty': "Le fichier est vide.",
                'max_length': "Le nom du fichier est trop long."
            }
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(
                    self.error_messages['image']['file_too_large'],
                    code='file_too_large'
                )
            try:
                # Vérifier que c'est une image valide
                Image.open(image).verify()
            except:
                raise forms.ValidationError(
                    self.error_messages['image']['invalid_image'],
                    code='invalid_image'
                )
        return image

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if video.size > 100 * 1024 * 1024:  # 100MB
                self.add_error('video', "La vidéo ne doit pas dépasser 100MB")
                raise forms.ValidationError("La vidéo ne doit pas dépasser 100MB")
            if not video.content_type.startswith('video/'):
                self.add_error('video', "Le fichier doit être une vidéo valide")
                raise forms.ValidationError("Le fichier doit être une vidéo valide")
            return video
        return None

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            if fichier.size > 20 * 1024 * 1024:  # 20MB
                self.add_error('fichier', "Le fichier ne doit pas dépasser 20MB")
                raise forms.ValidationError("Le fichier ne doit pas dépasser 20MB")
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'application/vnd.ms-powerpoint',
                           'application/vnd.openxmlformats-officedocument.presentationml.presentation']
            if fichier.content_type not in allowed_types:
                self.add_error('fichier', "Le type de fichier n'est pas supporté")
                raise forms.ValidationError("Le type de fichier n'est pas supporté")
            return fichier
        return None

    def __init__(self, *args, **kwargs):
        matiere_id = kwargs.pop('matiere_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les chapitres si une matière est spécifiée
        if matiere_id:
            self.fields['chapitre'].queryset = Chapitre.objects.filter(
                matiere_id=matiere_id,
                status=True
            )

        # Personnalisation des champs
        self.fields['chapitre'].widget.attrs.update({'class': 'form-control'})
        self.fields['titre'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['objectifs'].widget.attrs.update({'class': 'form-control'})
        self.fields['prerequis'].widget.attrs.update({'class': 'form-control'})
        self.fields['duree'].widget.attrs.update({
            'class': 'form-control',
            'min': '0',
            'placeholder': 'Durée en minutes'
        })
        self.fields['ordre'].widget.attrs.update({'class': 'form-control', 'min': '1'})
        self.fields['image'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'image/*'
        })
        self.fields['video'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'video/*'
        })
        self.fields['fichier'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': '.pdf,.doc,.docx,.ppt,.pptx'
        })

class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom', 'image', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Description de la matière...'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la matière'
            })
        }
        error_messages = {
            'image': {
                'invalid_image': "Le fichier n'est pas une image valide.",
                'invalid': "Format d'image non supporté.",
                'empty': "Le fichier image est vide.",
                'max_length': "Le nom du fichier est trop long.",
                'file_too_large': "L'image ne doit pas dépasser 5MB."
            }
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(
                    self.error_messages['image']['file_too_large'],
                    code='file_too_large'
                )
            try:
                # Vérifier que c'est une image valide
                Image.open(image).verify()
            except:
                raise forms.ValidationError(
                    self.error_messages['image']['invalid_image'],
                    code='invalid_image'
                )
        return image
