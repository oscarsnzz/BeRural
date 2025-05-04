from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),

    ## Be Rural
    path('add_review/<int:pk>/<str:model_type>/', views.add_review, name='add_review'),
    path('Registro/', views.UsuarioCreate.as_view(), name='Registro'),
    path('accounts/login/', views.login_view , name='login'),

    ##Pueblos principales
    path('pueblos/', views.pueblos, name='pueblos_principal'),

    ## aqui se ve el pueblo detail
    path('pueblo/<slug:slug>/', views.PuebloDetailView.as_view() , name='pueblo_detail'),

    ##aqui se ven todos los pueblos que tiene una comunidad 
    path('pueblos_por_comunidad/<str:comunidad_id>/', views.pueblos_por_comunidad, name='pueblos_por_comunidad'),
    ##editar pueblo
    path("gestor/pueblo/editar/<slug:slug>/", views.editar_pueblo, name="editar-pueblo"),

    ## chats 
    path('chat/', views.chat_view, name='chat'),  # público
    path('chat/<str:chatroom_name>/', views.chat_view, name='start-chat'),  # privado
    path('chat/pueblo/<slug:slug>/', views.chat_con_pueblo_view, name='chat-con-pueblo'),
    path("gestor/chats/", views.chats_para_gestor, name="gestor-chats"),

    ## Perfil
    path('perfil/', views.perfil, name='perfil'),
    
    ## Mudanza
    path('mudanza/',                  views.mudanza,     name='mudanza'),
    path('mudanza/add/',              views.add_tarea,   name='add_tarea'),
    path('mudanza/<int:pk>/toggle/',  views.toggle_tarea, name='toggle_tarea'),
    path('mudanza/<int:pk>/edit/',  views.edit_tarea,    name='edit_tarea'),
    path('mudanza/<int:pk>/delete/',views.delete_tarea,  name='delete_tarea'),

    # urls.py
    path("solicitar-reset-password/", views.solicitar_reset_password, name="solicitar-reset-password"),
    path("reset-password/<str:token>/", views.resetear_password, name="reset-password"),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)