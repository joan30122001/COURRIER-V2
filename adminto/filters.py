import django_filters
from .models import *
from django import forms



# class CourrierFilter(django_filters.FilterSet):
#     # code = django_filters.CharFilter(lookup_expr='iexact')
#     # class Meta:
#     #     model = Courrier
#     #     fields = ['code', 'objet']
#     code = django_filters.CharFilter(lookup_expr='icontains', label='Code', widget = forms.TextInput(attrs={'class': 'form-control ', 'size': 10}))
#     types = django_filters.CharFilter(lookup_expr='icontains', label='Type', widget = forms.TextInput(attrs={'class': 'form-control ', 'size': 20}))
#     objet = django_filters.CharFilter(lookup_expr='icontains', label='Objet', widget = forms.TextInput(attrs={'class': 'form-control ', 'size': 42}))


class CourrierFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'size': 10,
            'placeholder': 'Entrer le code'
        })
    )

    types = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Type',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'size': 20,
            'placeholder': 'Entrer le type'
        })
    )

    objet = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Objet',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'size': 42,
            'placeholder': "Entrer l'objet"
        })
    )

    class Meta:
        model = Courrier
        fields = ['code', 'types', 'objet']