from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from . import models
from .models import Pueblo, Usuario, TareaMudanza

# ------------------- Inline de TareaMudanza -------------------
class TareaMudanzaInline(admin.TabularInline):
    model = TareaMudanza
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


# ------------------- Usuario personalizado -------------------
class UsuarioAdmin(BaseUserAdmin):
    model = Usuario
    list_display = (
        'email','name','apellidos','telefono',
        'is_staff','is_superuser','mostrar_es_gestor'
    )
    list_filter = ('is_staff','is_superuser')
    search_fields = ('email','name','apellidos')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email','password')}),
        (_('Información personal'), {
            'fields': ('name','apellidos','telefono')
        }),
        (_('Permisos'), {
            'fields': (
                'is_active','is_staff','is_superuser',
                'groups','user_permissions'
            )
        }),
        (_('Fechas importantes'), {
            'fields': ('last_login',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email','name','apellidos','telefono',
                'password1','password2','is_staff','is_superuser'
            ),
        }),
    )

    def delete_model(self, request, obj):
        obj.mensajes.all().delete()
        super().delete_model(request, obj)

    def mostrar_es_gestor(self, obj):
        return obj.es_gestor
    mostrar_es_gestor.boolean = True
    mostrar_es_gestor.short_description = "Es gestor"

    # Aquí incluimos el inline de mudanzas:
    inlines = (TareaMudanzaInline,)


admin.site.register(Usuario, UsuarioAdmin)

# ------------------- Otros modelos -------------------

@admin.register(models.Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name','description','image')
    list_filter = ('name',)
    search_fields = ('name','description')

@admin.register(models.Cruise)
class CruiseAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    list_filter = ('name',)
    search_fields = ('name','description')

@admin.register(models.InfoRequest)
class InfoRequestAdmin(admin.ModelAdmin):
    list_display = ('name','email','cruise')
    list_filter = ('cruise',)
    search_fields = ('name','email')

@admin.register(Pueblo)
class PuebloAdmin(admin.ModelAdmin):
    list_display = ('name','ubicacion','habitantes')
    search_fields = ('name','ubicacion')

admin.site.register(models.Review)
admin.site.register(models.ChatGroup)
admin.site.register(models.GroupMessage)

@admin.register(TareaMudanza)
class TareaMudanzaAdmin(admin.ModelAdmin):
    list_display  = ('nombre','usuario','completada','created_at')
    list_filter   = ('usuario','completada')
    search_fields = ('nombre','usuario__email','usuario__name')
    ordering      = ('usuario','orden')
