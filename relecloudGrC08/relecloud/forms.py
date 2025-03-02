from django import forms
from .models import InfoRequest, Destination, Review
from django.core.exceptions import ValidationError


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


from django import forms
from .models import Usuario
from django.contrib.auth.hashers import make_password


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repite la contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['name', 'apellidos', 'telefono', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        # Asumiendo que Usuario es un modelo que extiende a User o tiene un campo email único
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
        usuario.password = make_password(self.cleaned_data['password'])  # Usar make_password para encriptar la contraseña
        if commit:
            usuario.save()
        return usuario

from django.contrib.auth.hashers import check_password

class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Intenta encontrar un usuario que coincida con el correo electrónico proporcionado
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise forms.ValidationError("No existe una cuenta con este correo electrónico.")

        # Verifica que la contraseña coincide con la guardada en la base de datos
        if not check_password(password, usuario.password):
            print(usuario.password)
            raise forms.ValidationError("Contraseña incorrecta.")

        # Guarda el usuario en el formulario para usarlo más adelante en la vista
        self.usuario = usuario

    def get_user(self):
        return self.usuario if hasattr(self, 'usuario') else None

from django import forms
from django.contrib.auth.hashers import check_password
from .models import Usuario

class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Aquí capturamos al usuario por email
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise forms.ValidationError("No existe un usuario con este correo electrónico.")

        # Comprobamos la contraseña
        if not check_password(password, usuario.password):
            raise forms.ValidationError("Contraseña incorrecta.")

        # Si todo está correcto, guardamos el usuario en el formulario para usarlo más adelante
        self.cleaned_data['usuario'] = usuario
        return self.cleaned_data
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    emailusu = forms.EmailField(label='Correo Electrónico')
    passwordusu = forms.CharField(label='Contraseña', widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(emailusu=email, passwordusu=password)
            if not user:
                raise forms.ValidationError("Correo electrónico o contraseña incorrecta.")
            if not user.is_active:
                raise forms.ValidationError("Esta cuenta está desactivada.")
        return self.cleaned_data
