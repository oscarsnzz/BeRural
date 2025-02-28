from django.contrib import admin
from . import models

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
