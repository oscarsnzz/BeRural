from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate



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
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Crea una contraseña'})
    )
    password2 = forms.CharField(
        label='Repite la contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña'})
    )

    class Meta:
        model = Usuario
        fields = ['name', 'apellidos', 'telefono', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Tus apellidos'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])  # Encripta la contraseña correctamente
        if commit:
            usuario.save()
        return usuario


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Tu contraseña'})
    )

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


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Introduce tu correo electrónico")



class CambiarPasswordForm(forms.Form):
    password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Introduce tu nueva contraseña'})
    )
    password2 = forms.CharField(
        label='Repite la nueva contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la nueva contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['name', 'apellidos', 'telefono', 'foto_perfil']