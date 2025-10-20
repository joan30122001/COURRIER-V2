import datetime
from django.db import models
from django.http import request
from adminto.models import *
from django import forms
from django.utils.safestring import mark_safe  # import pour mettre une url dans le help text
from django.contrib import messages


class RegistrationForm(forms.ModelForm):
    """ Formulaire pour la première phase d'enregistrement du Courrier """
    # Surchage de la classe
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Code qui permet de rendre obligatoire certains champs au niveau HTML
        for field in self.Meta.required:
            self.fields[field].required = True
    

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        if date and date != date.today():
            raise forms.ValidationError("")
        return cleaned_data


    class Meta:

        model = Courrier
        fields = (
            'emetteur', 'recepteur', 'code', 'date', 'objet', 'annee', 'structure', 'types'
        )
        widgets = {
            'emetteur': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Emetteur du courrier...',}),
            'recepteur': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Recepteur du courrier...'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code du courrier...'}),
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Date de dépôt du courrier...'}),
            'annee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Année de dépôt du courrier...'}),
            'objet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objet du courrier...'}),
            'structure': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Struture en charge du courrier...'}),
            'types': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Type du courrier...'}),
        }

        required = (
            'code','objet', 'types'
        )
        
        help_texts = {
            'emetteur':("Sélectionnez l'emetteur du courrier"), 
            'recepteur':("Sélectionnez le recepteur du courrier"), 
            'code':("Saisissez le code d'enregistrement du courrier Ex: 1"), 
            'date':("Saisissez la date d'enregistrement du courrier"), 
            'annee':("Saisissez l'année de dépôt du courrier"), 
            'objet':("Saisissez l'objet du courrier"),
            'structure':("Sélectionnez la structure en charge du courrier"),
            'types':("Sélectionnez le type du courrier"),
        }



class MentionForm(forms.ModelForm):
    """ Formulaire pour la deuxième phase d'enregistrement du Courrier """
    # Surchage de la classe
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Code qui permet de rendre obligatoire certains champs au niveau HTML
        for field in self.Meta.required:
            self.fields[field].required = True


    class Meta:

        model = Courrier
        fields = (
            'mention', 'service_traitement'
        )
        widgets = {
            'mention': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Mention du courrier...',}),
            'service_traitement': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Service de traitement du courrier...'}),
        }

        required = (
            'mention','service_traitement'
        )
        
        help_texts = {
            'mention':("Sélectionnez la mention du courrier"), 
            'service_traitement':("Sélectionnez le service de traitement du courrier"), 
        }



class ScanForm(forms.ModelForm):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        
    #     # allow passing a filtered queryset from the view
    #     courrier_qs = kwargs.pop('courrier_qs', None)
    #     super().__init__(*args, **kwargs)

    #     # Code qui permet de rendre obligatoire certains champs au niveau HTML
    #     for field in self.Meta.required:
    #         self.fields[field].required = True

    #     if courrier_qs is not None:
    #         self.fields['courrier'].queryset = courrier_qs

    #     # Make the select show the code (default label will use Courrier.__str__ if defined)
    #     self.fields['courrier'].label = "Code du courrier"


    def __init__(self, *args, **kwargs):
        # POP BEFORE super(); and call super() ONCE
        courrier_qs = kwargs.pop('courrier_qs', None)
        super().__init__(*args, **kwargs)

        # mark required in HTML
        for field in self.Meta.required:
            self.fields[field].required = True

        # filter choices if provided
        if courrier_qs is not None:
            self.fields['courrier'].queryset = courrier_qs

        # show the code in the dropdown items
        self.fields['courrier'].label_from_instance = lambda obj: obj.code
    
    class Meta:
        model = Scan
        fields = [
            'name', 
            'file',
            'courrier',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du courrier...'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Objet du courrier...'}),
            'courrier': forms.Select(attrs={'class': 'form-control js-courrier-search', 'placeholder': 'Code du courrier...'}),
        }

        required = (
            'name','file', 'courrier'
        )
        
        help_texts = {
            'name':("Saisissez un titre pour le courrier"), 
            'file':("Sélectionnez un fichier (image ou pdf)"), 
            'courrier':("Sélectionnez le code du courrier"),
        }