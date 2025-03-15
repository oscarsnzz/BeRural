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

def add_review(request, pk, model_type):
    if model_type == 'destination':
        related_model = get_object_or_404(Destination, pk=pk)
    elif model_type == 'cruise':
        related_model = get_object_or_404(models.Cruise, pk=pk)
    else:
        return redirect('/')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            if rating < 1 or rating > 5:
                return redirect(related_model.get_absolute_url())
            review = form.save(commit=False)
            if model_type == 'destination':
                review.destination = related_model
            elif model_type == 'cruise':
                review.cruise = related_model
            review.save()
            return redirect(related_model.get_absolute_url())
    return redirect('/')

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

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Usuario

from django.shortcuts import render, redirect
from .models import Usuario
from django.contrib.auth import login

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.password == password:  # Comparación en texto plano
                login(request, usuario)  # Iniciar sesión manualmente
                return redirect('pueblos_principal')  # Redirigir a la vista correcta
            else:
                return render(request, 'login_form.html', {'error': 'Correo electrónico o contraseña incorrecta.'})
        except Usuario.DoesNotExist:
            return render(request, 'login_form.html', {'error': 'Correo electrónico o contraseña incorrecta.'})
    
    return render(request, 'login_form.html')

from django.shortcuts import render
from .models import Pueblos

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
    
    pueblos_list = Pueblos.objects.all()  # Obtener todos los pueblos
    return render(request, 'Pueblos_Principal.html', {'pueblos': pueblos_list})


    return render(request, 'Pueblos_Principal.html', {
        'destinations': destinations_list,
        'show_all': show_all,
    })
