from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class Destination(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    description = models.TextField(max_length=2000, null=False, blank=False)
    image = models.ImageField(
        upload_to='destinations/',  # Carpeta dentro de MEDIA_ROOT donde se guardarán las imágenes
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("destination_detail", kwargs={"pk": self.pk})

    def has_image(self):
        """Check if the destination has an image."""
        return bool(self.image)

    def calculate_popularity(self):
        """Calcula la popularidad basada en el promedio de las valoraciones."""
        average_rating = self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        return average_rating

class Cruise(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    description = models.TextField(max_length=2000, null=False, blank=False)
    destinations = models.ManyToManyField(
        Destination,
        related_name='cruises'
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("cruise_detail", kwargs={"pk": self.pk})
    
class InfoRequest(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField()
    notes = models.TextField(max_length=2000, null=False, blank=False)
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT
    )


## LO DE PUEBLOS 

class Comunidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
    
from django.utils.text import slugify

class Pueblo(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    ubicacion = models.CharField(max_length=255)
    habitantes = models.IntegerField()
    descripcion = models.TextField()
    servicios = models.TextField()
    actividades = models.TextField()
    incentivos = models.TextField()
    image = models.ImageField(
        upload_to='destinations/',  # Carpeta dentro de MEDIA_ROOT donde se guardarán las imágenes
        null=True,
        blank=True
    )    
    comunidad = models.ForeignKey(
        Comunidad, 
        on_delete=models.CASCADE, 
        related_name='pueblos', 
    )
    slug = models.SlugField(unique=True, blank=True, null=True)  # Slug para URL


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

    def calculate_popularity(self):
        """Calcula la popularidad basada en el promedio de las valoraciones."""
        average_rating = self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        return average_rating




class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 5)]  # Ratings from 1 to 5

    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        null=True, 
        blank=True
    )
    cruise = models.ForeignKey(
        Cruise, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        null=True, 
        blank=True
    )

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
        if self.destination:
            return f'Review for Destination: {self.destination.name} - Rating: {self.rating}'
        elif self.cruise:
            return f'Review for Cruise: {self.cruise.name} - Rating: {self.rating}'
        elif self.pueblo:
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
        usuario.set_password(password)  # Guardar la contraseña encriptada
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser):
    name = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'apellidos']

    objects = UsuarioManager()

    def __str__(self):
        return self.email
