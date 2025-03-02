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



from django.shortcuts import render, redirect
from .forms import UsuarioForm

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    show_all = request.GET.get('show_all', 'false') == 'true'  # Leer parámetro de URL
    all_destinations = Destination.objects.annotate(average_rating=Avg('reviews__rating'))
    if show_all:
        destinations_list = all_destinations
    else:
        # Filtrar y ordenar por la valoración promedio de mayor a menor
        destinations_list = all_destinations.filter(average_rating__isnull=False).order_by('-average_rating')[:3]

    # Preparar las estrellas para cada destino
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

        # Calcular estrellas llenas y vacías para el promedio general
        context['full_stars'] = range(int(average_rating))
        context['empty_stars'] = range(5 - int(average_rating))
        context['average_rating'] = average_rating

        # Procesar cada review para incluir estrellas llenas y vacías
        for review in reviews:
            review.full_stars = range(review.rating)
            review.empty_stars = range(5 - review.rating)

        context['reviews'] = reviews
        context['review_form'] = ReviewForm()
        return context

class DestinationCreateView(generic.CreateView):
    model = models.Destination
    template_name = 'destination_form.html'
    fields = ['name', 'description', 'image']  # Incluimos el campo "image"

class DestinationUpdateView(generic.UpdateView):
    model = models.Destination
    template_name = 'destination_form.html'
    fields = ['name', 'description', 'image']  # Incluimos el campo "image"
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

        # Preparar estrellas promedio
        context['full_stars'] = range(int(average_rating))
        context['empty_stars'] = range(5 - int(average_rating))
        context['average_rating'] = average_rating

        # Preparar estrellas para cada review
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
        # Enviar el correo electrónico
        send_mail(
            subject=f'Muchas gracias {form.instance.name}',
            message=(
                f"Gracias, {form.instance.name}, por tu Registro.\n\n"
                f"Tu cuenta ha sido registrada con exito "
                "Desde el equipo de Be rural le agradecemos por usar nuestra aplicacion."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[form.instance.email],
            fail_silently=False,
        )
        return response

# def add_review(request, pk, model_type):
#     if model_type == 'destination':
#         related_model = get_object_or_404(Destination, pk=pk)
#     elif model_type == 'cruise':
#         related_model = get_object_or_404(models.Cruise, pk=pk)
#     else:
#         return redirect('/')

#     if request.method == 'POST':
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             # Asignar los campos manualmente
#             if model_type == 'destination':
#                 review.destination = related_model
#             elif model_type == 'cruise':
#                 review.cruise = related_model
#             review.save()
#             return redirect(related_model.get_absolute_url())
#     return redirect('/')

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
                    return redirect(related_model.get_absolute_url())  # Rechazar valores fuera de rango
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
    form_class = UsuarioForm  # Usar el formulario personalizado
    template_name = 'Registro.html'
    success_url = reverse_lazy('index')  # Redirigir a 'index' tras un registro exitoso
    success_message = "Tu cuenta ha sido registrada con éxito. ¡Gracias por unirte!"

    def form_valid(self, form):
        # Lógica para enviar correo electrónico después de un registro exitoso
        response = super().form_valid(form)
        send_mail(
            subject=f"Bienvenido a la plataforma, {form.instance.name}",
            message=f"Hola, {form.instance.name}!\n\nTu cuenta ha sido registrada con éxito.\nGracias por usar nuestra aplicación.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[form.instance.email],
            fail_silently=False,
        )
        return response
    
# from django.contrib.auth import authenticate, login
# from django.contrib import messages
# from .forms import LoginForm

# class UsuarioLoginView(generic.FormView):
#     form_class = LoginForm  # Usa el formulario de inicio de sesión personalizado
#     template_name = 'login_form.html'
#     success_url = reverse_lazy('index')  # Redirige a 'index' después de un inicio de sesión exitoso

#     def form_valid(self, form):
#         email = form.cleaned_data['email']
#         password = form.cleaned_data['password']
#         usuario = authenticate(self.request, username=email, password=password)  # Asegúrate de que el modelo Usuario use 'email' como USERNAME_FIELD si es necesario.

#         if usuario is not None:
#             login(self.request, usuario)
#             messages.success(self.request, "Inicio de sesión exitoso. ¡Bienvenido de nuevo!")
#             return super().form_valid(form)
#         else:
#             messages.error(self.request, "Correo electrónico o contraseña incorrecta.")
#             return redirect('login')  # Cambia 'login' por el nombre de ruta que corresponda al login.

#     def form_invalid(self, form):
#         messages.error(self.request, "Error en el formulario. Por favor corrige los errores e intenta de nuevo.")
#         return super().form_invalid(form)


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:  # Asegurándonos de que ambos, email y contraseña, estén presentes
            usuario = authenticate(request, username=email, password=password)
            if usuario is not None:
                login(request, usuario)
                return redirect('index')
            else:
                # Considera enviar el formulario de nuevo con un mensaje de error.
                return render(request, 'login_form.html', {
                    'error': 'Correo electrónico o contraseña incorrecta.'
                })
        else:
            # Maneja el caso donde uno o ambos campos son vacíos
            return render(request, 'login_form.html', {
                'error': 'Debes llenar ambos campos.'
            })

    # GET request: Mostrar formulario vacío
    return render(request, 'login_form.html')
