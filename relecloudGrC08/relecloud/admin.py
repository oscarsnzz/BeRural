from django.contrib import admin
from . import models
from django.contrib import admin
from .models import Pueblo  # Importa el modelo

from django.contrib import admin
from .models import Pueblo



# Personalizamos la visualización de Destination en el panel de administración
@admin.register(models.Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')  # Mostramos los campos principales
    list_filter = ('name',)  # Filtramos por nombre
    search_fields = ('name', 'description')  # Habilitamos la búsqueda por nombre y descripción

# Registramos Cruise y InfoRequest sin personalización adicional
@admin.register(models.Cruise)
class CruiseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Mostramos los campos principales
    list_filter = ('name',)
    search_fields = ('name', 'description')

@admin.register(models.InfoRequest)
class InfoRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'cruise')  # Mostramos los campos principales
    list_filter = ('cruise',)
    search_fields = ('name','email')


admin.site.register(models.Review)


@admin.register(models.Usuario)  # Utiliza el decorador para registrar el modelo
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'apellidos', 'telefono', 'email', 'password')  # Campos que quieres mostrar en la lista
    search_fields = ('name', 'apellidos', 'email')  # Campos por los que se puede buscar


@admin.register(Pueblo)
class PuebloAdmin(admin.ModelAdmin):
    list_display = ('name', 'ubicacion', 'habitantes')  # Campos visibles en el panel
    search_fields = ('name', 'ubicacion')  # Habilitar búsqueda

