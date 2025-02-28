from django import forms
from .models import InfoRequest, Destination, Review

class InfoRequestForm(forms.ModelForm):
    class Meta:
        model = InfoRequest
        fields = ['name', 'email', 'cruise', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'cruise': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional Notes'}),
        }

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['name', 'description', 'image']  # Añadimos el campo de imagen
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        }


# #Codigo destinado a las reviews
# class ReviewForm(forms.ModelForm):
#     class Meta:
#         model = Review
#         fields = ['rating', 'comment']
#         widgets = {
#             'rating': forms.Select(attrs={'class': 'form-control'}),
#             'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your comment here...'}),
#         }


class StarRatingWidget(forms.RadioSelect):
    template_name = 'widgets/star_rating.html'  # Debes crear esta plantilla

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            #'rating': StarRatingWidget(attrs={'class': 'star-rating'}),
            'rating': forms.HiddenInput(), 
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your comment here...'}),
        }

        
