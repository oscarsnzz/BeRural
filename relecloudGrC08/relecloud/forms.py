from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

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
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        }

class StarRatingWidget(forms.RadioSelect):
    template_name = 'widgets/star_rating.html'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your comment here...'}),
        }

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repite la contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['name', 'apellidos', 'telefono', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])  # Encriptar correctamente la contraseña
        if commit:
            usuario.save()
        return usuario

class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        usuario = authenticate(username=email, password=password)
        if not usuario:
            raise ValidationError("Correo electrónico o contraseña incorrecta.")

        cleaned_data['usuario'] = usuario
        return cleaned_data

    def get_user(self):
        return self.cleaned_data.get('usuario')
    
class ChatMessageCreateForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Escribe tu mensaje...',
                'class': 'w-4/5 rounded-xl p-2 text-black',
                'autocomplete': 'off',
            }),
        }


class PuebloForm(forms.ModelForm):
    class Meta:
        model = Pueblo
        fields = ['name', 'descripcion', 'servicios', 'actividades', 'incentivos', 'image']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'servicios': forms.Textarea(attrs={'rows': 3}),
            'actividades': forms.Textarea(attrs={'rows': 3}),
            'incentivos': forms.Textarea(attrs={'rows': 3}),
        }
        
        
class TareaMudanzaForm(forms.ModelForm):
    class Meta:
        model  = TareaMudanza
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nueva tarea…',
                'required': True
            })
        }