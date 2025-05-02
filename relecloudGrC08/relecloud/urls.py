from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('destinations/', views.destinations, name='destinations'),
    path('destination/<int:pk>/', views.DestinationDetailView.as_view(), name='destination_detail'),
    path('destination/add/', views.DestinationCreateView.as_view(), name='destination_form'),
    path('destination/<int:pk>/update/', views.DestinationUpdateView.as_view(), name='destination_form'),
    path('destination/<int:pk>/delete/', views.DestinationDeleteView.as_view(), name='destination_confirm_delete'),
    path('cruise/<int:pk>/', views.CruiseDetailView.as_view(), name='cruise_detail'),
    path('info_request/', views.InfoRequestCreate.as_view(), name='info_request'),
    ##
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
    path('mudanza/toggle/<int:pk>/',  views.toggle_tarea, name='toggle_tarea'),
   

]