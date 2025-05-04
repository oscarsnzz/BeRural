from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import os

from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils.text import slugify

from cloudinary.models import CloudinaryField


## Be rural 
## LO DE PUEBLOS 

class Comunidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
    

class Pueblo(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    ubicacion = models.CharField(max_length=255)
    habitantes = models.IntegerField()
    descripcion = models.TextField()
    servicios = models.TextField()
    actividades = models.TextField()
    incentivos = models.TextField()
    # image = models.ImageField(
    #     upload_to='destinations/',  # Carpeta dentro de MEDIA_ROOT donde se guardarán las imágenes
    #     null=True,
    #     blank=True
    # )    
    image = CloudinaryField('image', null=True, blank=True)  # Usando Cloudinary para almacenar imágenes
    comunidad = models.ForeignKey(
        Comunidad, 
        on_delete=models.CASCADE, 
        related_name='pueblos', 
    )
    slug = models.SlugField(unique=True, blank=True, null=True)  # Slug para URL

    gestor = models.OneToOneField(
        'Usuario',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='pueblo_gestionado'
    )


    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("pueblo_detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Genera el slug a partir del nombre
        super().save(*args, **kwargs)

    def has_image(self):
        """Check if the destination has an image."""
        return bool(self.image)

    def get_absolute_url(self):
        return reverse("pueblo_detail", kwargs={"slug": self.slug})

    def calculate_popularity(self):
        """Calcula la popularidad basada en el promedio de las valoraciones."""
        average_rating = self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        return average_rating




class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 5)]  # Ratings from 1 to 5


    # # Eliminar esto 
    # destination = models.ForeignKey(
    #     Destination, 
    #     on_delete=models.CASCADE, 
    #     related_name='reviews', 
    #     null=True, 
    #     blank=True
    # )
    # cruise = models.ForeignKey(
    #     Cruise, 
    #     on_delete=models.CASCADE, 
    #     related_name='reviews', 
    #     null=True, 
    #     blank=True
    # )


    # Aqui no borrar 
    pueblo = models.ForeignKey(
        Pueblo,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True
    )
    author = models.CharField(max_length=255, null=False, blank=False, default="Anonymus")
    comment = models.TextField(null=True, blank=True)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.pueblo:
            return f'Review for Pueblo: {self.pueblo.name} - Rating: {self.rating}'
        return 'Review'

    class Meta:
        ordering = ['-created_at']


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

# El modelo Usuario corregido
class Usuario(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_gestor=models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'apellidos']

    objects = UsuarioManager()

    def __str__(self):
        return self.email
    
    def delete(self, *args, **kwargs):
        self.mensajes.all().delete()
        super().delete(*args, **kwargs)

    @property
    def es_gestor(self):
        return self.groups.filter(name="Gestores").exists()

import shortuuid

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True, default=shortuuid.uuid)
    users_online = models.ManyToManyField(Usuario, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(Usuario, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='mensajes')
    body = models.CharField(max_length=300)
    author = models.ForeignKey(
    Usuario,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='mensajes'
)

    created = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        author_name = self.author.name if self.author else "Anónimo"
        return f'{author_name} - {self.body}'

    
    class Meta:
        ordering = ['created']  
        
        
class TareaMudanza(models.Model):
    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE)
    nombre     = models.CharField(max_length=200)
    completada = models.BooleanField(default=False)
    orden      = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.nombre