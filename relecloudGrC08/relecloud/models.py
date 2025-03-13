from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


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
        return 'Review'

    class Meta:
        ordering = ['-created_at']


from django.db import models
from django.contrib.auth.hashers import make_password

class Usuario(models.Model):
    name = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)  # Asegúrate de que el correo sea único
    password = models.CharField(max_length=128)  # Almacenar las contraseñas encriptadas

    def save(self, *args, **kwargs):
        self.password = (self.password)  # Encriptar la contraseña
        super().save(*args, **kwargs)  # Llamar al método save del padre para guardar en la base de datos

    def __str__(self):
        return f"{self.name} {self.apellidos}"

class Pueblos(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    description = models.TextField(max_length=2000, null=False, blank=False)
    image = models.ImageField(
        upload_to='pueblos/',  # Carpeta dentro de MEDIA_ROOT donde se guardarán las imágenes
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
