from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from . import models
from .models import Destination, Cruise, Review
from django.db.models import Avg
from .forms import ReviewForm
from django.views.generic.edit import UpdateView
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.conf import settings
from .forms import UsuarioForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Usuario
from .models import Pueblo
from .models import ChatGroup, GroupMessage
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    show_all = request.GET.get('show_all', 'false') == 'true'  
    all_destinations = Destination.objects.annotate(average_rating=Avg('reviews__rating'))
    if show_all:
        destinations_list = all_destinations
    else:
        destinations_list = all_destinations.filter(average_rating__isnull=False).order_by('-average_rating')[:3]

    for destination in destinations_list:
        full_stars = int(destination.average_rating or 0)
        empty_stars = 5 - full_stars
        destination.stars_full = range(full_stars)
        destination.stars_empty = range(empty_stars)

    return render(request, 'destinations.html', {
        'destinations': destinations_list,
        'show_all': show_all,
    })

class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destination = self.get_object()
        reviews = models.Review.objects.filter(destination=destination)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        context['full_stars'] = range(int(average_rating))
        context['empty_stars'] = range(5 - int(average_rating))
        context['average_rating'] = average_rating

        for review in reviews:
            review.full_stars = range(review.rating)
            review.empty_stars = range(5 - review.rating)

        context['reviews'] = reviews
        context['review_form'] = ReviewForm()
        return context

class DestinationCreateView(generic.CreateView):
    model = models.Destination
    template_name = 'destination_form.html'
    fields = ['name', 'description', 'image']

class DestinationUpdateView(generic.UpdateView):
    model = models.Destination
    template_name = 'destination_form.html'
    fields = ['name', 'description', 'image']
    success_url = reverse_lazy('destinations')

class DestinationDeleteView(generic.DeleteView):
    model = models.Destination
    template_name = 'destination_confirm_delete.html'
    success_url = reverse_lazy('destinations')

class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cruise = self.get_object()
        reviews = Review.objects.filter(cruise=cruise)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        context['full_stars'] = range(int(average_rating))
        context['empty_stars'] = range(5 - int(average_rating))
        context['average_rating'] = average_rating

        for review in reviews:
            review.full_stars = range(review.rating)
            review.empty_stars = range(5 - review.rating)

        context['reviews'] = reviews
        context['review_form'] = ReviewForm()
        return context

class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'

    def form_valid(self, form):
        response = super().form_valid(form)
        send_mail(
            subject=f'Muchas gracias {form.instance.name}',
            message=(
                f"Gracias, {form.instance.name}, por tu Registro.\n\n"
                f"Tu cuenta ha sido registrada con éxito. "
                "Desde el equipo de Be Rural le agradecemos por usar nuestra aplicación."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[form.instance.email],
            fail_silently=False,
        )
        return response
    

### RESEÑAS DE LOS PUEBLOS
def add_review(request, pk, model_type):
    
    if model_type == 'pueblo':
        related_model = get_object_or_404(models.Pueblo, pk=pk)
    else:
        return redirect('/pueblos/')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            if rating < 1 or rating > 5:
                return redirect(related_model.get_absolute_url())
            review = form.save(commit=False)
            
            if model_type == 'pueblo':   
                review.pueblo = related_model

            review.save()
            return redirect(related_model.get_absolute_url())
    return redirect('/pueblos')

class UsuarioCreate(SuccessMessageMixin, generic.CreateView):
    model = models.Usuario
    form_class = UsuarioForm
    template_name = 'Registro.html'
    success_url = reverse_lazy('index')
    success_message = "Tu cuenta ha sido registrada con éxito. ¡Gracias por unirte!"

    def form_valid(self, form):
        response = super().form_valid(form)
        send_mail(
            subject=f"Bienvenido a la plataforma, {form.instance.name}",
            message=f"Hola, {form.instance.name}!\n\nTu cuenta ha sido registrada con éxito.\nGracias por usar nuestra aplicación.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[form.instance.email],
            fail_silently=False,
        )
        return response


# ### LOGIN para los usuarios 
# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         usuario = authenticate (request, email=email, password=password)  # Autenticación del usuario
#         if usuario is not None:
#             login(request, usuario)
#             return redirect('pueblos_principal')  # Redirigir a la vista correcta
        
#         # try:
#         #     usuario = Usuario.objects.get(email=email)
#         #     if usuario.password == password:  # Comparación en texto plano
#         #         login(request, usuario)  # Iniciar sesión manualmente
#         #         return redirect('pueblos_principal')  # Redirigir a la vista correcta
#         #     else:
#         #         return render(request, 'login_form.html', {'error': 'Correo electrónico o contraseña incorrecta.'})
#         # except Usuario.DoesNotExist:
#         #     return render(request, 'login_form.html', {'error': 'Correo electrónico o contraseña incorrecta.'})
    
#     return render(request, 'login_form.html')

from django.contrib.auth import login
from .forms import LoginForm

def login_view(request):
    from django.contrib import messages  # para mostrar mensajes si no lo tienes ya
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect(request.GET.get('next', 'pueblos_principal'))
        else:
            messages.error(request, "Credenciales inválidas. Intenta de nuevo.")
            print("Errores del formulario:", form.errors)  # <--- Imprime errores en consola
    else:
        form = LoginForm()

    return render(request, 'login_form.html', {'form': form})




def pueblos(request):
    show_all = request.GET.get('show_all', 'false') == 'true'
    all_destinations = Destination.objects.annotate(average_rating=Avg('reviews__rating'))
    if show_all:
        destinations_list = all_destinations
    else:
        destinations_list = all_destinations.filter(average_rating__isnull=False).order_by('-average_rating')[:3]

    for destination in destinations_list:
        full_stars = int(destination.average_rating or 0)
        empty_stars = 5 - full_stars
        destination.stars_full = range(full_stars)
        destination.stars_empty = range(empty_stars)
    
    pueblos_list = Pueblo.objects.all()  # Obtener todos los pueblos
    return render(request, 'Pueblos_Principal.html', {'pueblos': pueblos_list})


class PuebloDetailView(generic.DetailView):
    template_name = 'pueblo_detail.html'
    model = Pueblo
    context_object_name = 'pueblo'
    slug_field = "slug"  # Django buscará por este campo
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pueblo = self.get_object()
        
        # Obtener todas las reseñas del pueblo
        reviews = Review.objects.filter(pueblo=pueblo)
        
        # Calcular el promedio de las calificaciones
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # Generar rangos para mostrar estrellas llenas y vacías
        context['full_stars'] = range(int(average_rating))
        context['empty_stars'] = range(5 - int(average_rating))
        context['average_rating'] = average_rating

        # Ajustar estrellas en cada reseña
        for review in reviews:
            review.full_stars = range(review.rating)
            review.empty_stars = range(5 - review.rating)

        context['reviews'] = reviews
        context['review_form'] = ReviewForm()
        return context

from django.shortcuts import render
from .models import Pueblo, Comunidad

def pueblos_por_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    pueblos = Pueblo.objects.filter(comunidad=comunidad)  # Obtener los pueblos de esa comunidad
    
    return render(request, 'pueblos_por_comunidad.html', {
        'comunidad': comunidad,
        'pueblos': pueblos
    })


class UsuarioCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'Registro.html'
    model = Usuario
    form_class = UsuarioForm
    success_url = reverse_lazy('login')  # redirige al login tras registrarse
    success_message = "Gracias, %(name)s. Tu cuenta ha sido registrada con éxito."

    def form_valid(self, form):
        response = super().form_valid(form)
        send_mail(
            subject=f"Bienvenido/a a Be Rural, {form.instance.name}",
            message=(
                f"Hola {form.instance.name},\n\n"
                "Tu cuenta ha sido creada con éxito.\n"
                "Gracias por formar parte de Be Rural ✨"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[form.instance.email],
            fail_silently=False,
        )
        return response


from .forms import ChatMessageCreateForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatGroup, GroupMessage
from .forms import ChatMessageCreateForm
from django.http import Http404

@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    messages = chat_group.mensajes.all().order_by('-created')[:30][::-1]

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    mis_chats = request.user.chat_groups.filter(is_private=True)

    if request.method == 'POST':
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()

            if request.headers.get('HX-Request'):
                return render(request, 'chat_message.html', {
                    'message': message,
                    'user': request.user,
                    'just_added': True,
                })
            return redirect('chat')

    else:
        form = ChatMessageCreateForm()

    context = {
        'messages': messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'mis_chats': mis_chats,  # 👈 Aquí
    }

    return render(request, 'chat.html', context)

@login_required
def chat_con_pueblo_view(request, slug):
    pueblo = get_object_or_404(Pueblo, slug=slug)
    gestor = pueblo.gestor

    if request.user == gestor:
        return redirect('pueblos_principal')  # por si el gestor intenta hablar consigo mismo

    user_ids = sorted([str(request.user.id), str(gestor.id)])
    group_name = f"chat-{slug}-{'-'.join(user_ids)}"

    chat_group, created = ChatGroup.objects.get_or_create(
        group_name=group_name,
        defaults={"is_private": True}
    )
    chat_group.members.add(request.user, gestor)

    messages = chat_group.mensajes.all().order_by('-created')[:30][::-1]

    if request.method == 'POST':
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()

            if request.headers.get('HX-Request'):
                return render(request, 'chat_message.html', {
                    'message': message,
                    'user': request.user,
                    'just_added': True,
                })

            return redirect('chat-con-pueblo', slug=slug)

    else:
        form = ChatMessageCreateForm()

    return render(request, 'chat.html', {
        'messages': messages,
        'form': form,
        'user': request.user,
        'pueblo': pueblo,
        'gestor': gestor,
        'chatroom_name': group_name,
        'other_user': gestor if request.user != gestor else None
    })


def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('pueblos_principal')
    
    other_user = Usuario.objects.get(username = username)
    my_chatrooms = request.user.chat_groups.filter(is_private= True)

    if my_chatrooms.exist():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
            else:
                chatroom = ChatGroup.objects.create(is_private = True)
                chatroom.members.add(other_user, request.user)
    else:
        chatroom = ChatGroup.objects.create(is_private = True)
        chatroom.members.add(other_user, request.user)

    return redirect('start-chat', chatroom.group_name)

@login_required
def chats_para_gestor(request):
    if not request.user.es_gestor:
        return redirect('pueblos_principal')

    pueblo = getattr(request.user, 'pueblo_gestionado', None)
    if not pueblo:
        return render(request, 'chats_gestor.html', {'mis_chats': []})

    chats = ChatGroup.objects.filter(
        group_name__startswith=f'chat-{pueblo.slug}-',
        is_private=True,
        members=request.user  # el gestor debe estar en el grupo
    )

    return render(request, 'chats_gestor.html', {
        'mis_chats': chats,
        'pueblo': pueblo
    })
