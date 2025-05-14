from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from . import models
from .models import Review
from django.db.models import Avg
from .forms import ReviewForm
from django.views.generic.edit import UpdateView
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.conf import settings
from .forms import UsuarioForm, PuebloForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Usuario
from .models import Pueblo
from .models import ChatGroup, GroupMessage
from django.contrib.auth.decorators import login_required
from .models import TareaMudanza
from .forms import TareaMudanzaForm
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render
from .utils_llm import recuperar_contexto, llamar_llm_openrouter
from .forms import EditarPerfilForm
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

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

    return render(request, 'Login/login_form.html', {'form': form})




def pueblos(request):
    show_all = request.GET.get('show_all', 'false') == 'true'
    
    # Anotar cada pueblo con su media de valoraciones
    all_destinations = Pueblo.objects.annotate(average_rating=Avg('reviews__rating'))

    if show_all:
        destinations_list = all_destinations
    else:
        destinations_list = all_destinations.filter(average_rating__isnull=False).order_by('-average_rating')[:3]

    # Calcular estrellas para cada pueblo
    for destino in destinations_list:
        full_stars = int(destino.average_rating or 0)
        half_star = 1 if destino.average_rating and (destino.average_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        destino.stars_full = range(full_stars)
        destino.star_half = half_star
        destino.stars_empty = range(empty_stars)

    return render(request, 'Pueblos/Pueblos_Principal.html', {
        'pueblos': destinations_list  # pasamos la lista con anotaciones
    })


class PuebloDetailView(generic.DetailView):
    template_name = 'Pueblos/pueblo_detail.html'
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
    pueblos = Pueblo.objects.filter(comunidad=comunidad).annotate(average_rating=Avg('reviews__rating'))

    for pueblo in pueblos:
        avg = pueblo.average_rating or 0
        full_stars = int(avg)
        half_star = 1 if avg - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star

        pueblo.stars_full = range(full_stars)
        pueblo.star_half = half_star
        pueblo.stars_empty = range(empty_stars)

    return render(request, 'Pueblos/pueblos_por_comunidad.html', {
        'comunidad': comunidad,
        'pueblos': pueblos
    })


class UsuarioCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'Login/Registro.html'
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
                return render(request, 'Chats/chat_message.html', {
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

    return render(request, 'Chats/chat.html', context)

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
                return render(request, 'Chats/chat_message.html', {
                    'message': message,
                    'user': request.user,
                    'just_added': True,
                })

            return redirect('chat-con-pueblo', slug=slug)

    else:
        form = ChatMessageCreateForm()

    return render(request, 'Chats/chat.html', {
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
        return render(request, 'Chats/chats_gestor.html', {'mis_chats': []})

    chats = ChatGroup.objects.filter(
        group_name__startswith=f'chat-{pueblo.slug}-',
        is_private=True,
        members=request.user  # el gestor debe estar en el grupo
    )

    return render(request, 'Chats/chats_gestor.html', {
        'mis_chats': chats,
        'pueblo': pueblo
    })


@login_required
def editar_pueblo(request, slug):
    pueblo = get_object_or_404(Pueblo, slug=slug)

    if request.user != pueblo.gestor:
        return redirect('pueblos_principal')

    if request.method == "POST":
        form = PuebloForm(request.POST, request.FILES, instance=pueblo)
        if form.is_valid():
            form.save()
            return redirect('pueblo_detail', slug=pueblo.slug)
    else:
        form = PuebloForm(instance=pueblo)

    return render(request, 'Pueblos/Pueblos_editar.html', {'form': form, 'pueblo': pueblo})



@login_required  
def perfil(request):
    return render(request, 'perfil.html')



@login_required
def mudanza(request):
    tareas    = TareaMudanza.objects.filter(usuario=request.user).order_by('orden')
    completed = tareas.filter(completada=True).count()
    pending   = tareas.count() - completed
    return render(request, 'mudanza.html', {
        'tareas':    tareas,
        'completed': completed,
        'pending':   pending,
    })

@login_required
def add_tarea(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre','').strip()
        if nombre:
            TareaMudanza.objects.create(usuario=request.user, nombre=nombre)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tareas    = TareaMudanza.objects.filter(usuario=request.user).order_by('orden')
        completed = tareas.filter(completada=True).count()
        pending   = tareas.count() - completed
        lista = [
            {'id': t.pk, 'nombre': t.nombre, 'completada': t.completada}
            for t in tareas
        ]
        return JsonResponse({'completed': completed, 'pending': pending, 'tareas': lista})
    return redirect(reverse('mudanza') + '#lista')

@login_required
def toggle_tarea(request, pk):
    if request.method == 'POST':
        tarea = get_object_or_404(TareaMudanza, pk=pk, usuario=request.user)
        tarea.completada = not tarea.completada
        tarea.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tareas    = TareaMudanza.objects.filter(usuario=request.user).order_by('orden')
        completed = tareas.filter(completada=True).count()
        pending   = tareas.count() - completed
        lista = [{'id': t.pk, 'nombre': t.nombre, 'completada': t.completada} for t in tareas]
        return JsonResponse({'completed': completed, 'pending': pending, 'tareas': lista})
    return redirect(reverse('mudanza') + '#lista')

@login_required
def delete_tarea(request, pk):
    if request.method == 'POST':
        tarea = get_object_or_404(TareaMudanza, pk=pk, usuario=request.user)
        tarea.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tareas    = TareaMudanza.objects.filter(usuario=request.user).order_by('orden')
        completed = tareas.filter(completada=True).count()
        pending   = tareas.count() - completed
        lista = [{'id': t.pk, 'nombre': t.nombre, 'completada': t.completada} for t in tareas]
        return JsonResponse({'completed': completed, 'pending': pending, 'tareas': lista})
    return redirect(reverse('mudanza') + '#lista')

@login_required
def edit_tarea(request, pk):
    if request.method == 'POST':
        tarea = get_object_or_404(TareaMudanza, pk=pk, usuario=request.user)
        nombre = request.POST.get('nombre','').strip()
        if nombre:
            tarea.nombre = nombre
            tarea.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tareas    = TareaMudanza.objects.filter(usuario=request.user).order_by('orden')
        completed = tareas.filter(completada=True).count()
        pending   = tareas.count() - completed
        lista = [{'id': t.pk, 'nombre': t.nombre, 'completada': t.completada} for t in tareas]
        return JsonResponse({'completed': completed, 'pending': pending, 'tareas': lista})
    return redirect(reverse('mudanza') + '#lista')

# views.py
import uuid
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import PasswordResetRequestForm
from .models import Usuario  # O get_user_model()

reset_tokens = {}  # ⚠️ En producción usa una tabla con expiración

def solicitar_reset_password(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Usuario.objects.get(email=email)
                token = str(uuid.uuid4())
                reset_tokens[token] = user.id  # ⚠️ En producción: usar modelo
                link = request.build_absolute_uri(f"/reset-password/{token}/")
                send_mail(
                    "Recuperación de contraseña",
                    f"Hola, haz clic en este enlace para restablecer tu contraseña:\n{link}",
                    "noreply@berural.com",
                    [email],
                )
                return render(request, "Contrasena/mensaje_enviado.html")
            except Usuario.DoesNotExist:
                form.add_error('email', 'No existe un usuario con ese correo.')
    else:
        form = PasswordResetRequestForm()
    return render(request, "Contrasena/solicitar_reset_password.html", {"form": form})


# views.py
from .forms import CambiarPasswordForm

def resetear_password(request, token):
    user_id = reset_tokens.get(token)
    if not user_id:
        raise Http404("Token no válido o expirado")

    usuario = Usuario.objects.get(id=user_id)

    if request.method == "POST":
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            del reset_tokens[token]
            return redirect("login")
    else:
        form = CambiarPasswordForm()

    return render(request, "Contrasena/password_reset.html", {"form": form})

def chatbot_view(request):
    respuesta, pregunta = "", ""
    if request.method == "POST":
        pregunta = request.POST.get("pregunta", "")
        contexto = recuperar_contexto(pregunta)
        respuesta = llamar_llm_openrouter(contexto, pregunta)
    return render(request, "chatbot.html", {"pregunta": pregunta, "respuesta": respuesta})


def verificar_email(request):
    email = request.GET.get("email", "")
    existe = Usuario.objects.filter(email=email).exists()
    return JsonResponse({'exists': existe})


def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado correctamente!')
            return redirect('perfil')  # ✅ Redirige al perfil después de guardar
    else:
        form = EditarPerfilForm(instance=request.user)

    return render(request, 'editar_perfil.html', {'form': form})