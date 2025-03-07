from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm, PasswordResetForm, UserProfileForm, ProfileForm, ChangeUsernameForm, ChangePasswordForm, CollectionForm, EntryForm
from .models import Collection, Entry
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
import os

def home_view(request):
    """Vista para la página principal."""
    if request.user.is_authenticated:
        # Obtener las colecciones del usuario
        user_collections = Collection.objects.filter(user=request.user).order_by('-created_at')
        
        # Obtener entradas públicas de otros usuarios
        public_entries = Entry.objects.filter(visibility='public').exclude(user=request.user).order_by('-created_at')[:10]
        
        # Obtener entradas del usuario
        user_entries = Entry.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        return render(request, 'core/home.html', {
            'user_collections': user_collections,
            'public_entries': public_entries,
            'user_entries': user_entries
        })
    
    return render(request, 'core/home.html')

def register_view(request):
    """Vista para el registro de usuarios."""
    if request.user.is_authenticated:
        messages.info(request, 'Ya has iniciado sesión.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Eureka.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    """Vista para el inicio de sesión de usuarios."""
    if request.user.is_authenticated:
        messages.info(request, 'Ya has iniciado sesión.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña inválidos.')
    else:
        form = UserLoginForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """Vista para el cierre de sesión de usuarios."""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')

@login_required
def profile_view(request):
    """Vista para el perfil de usuario."""
    # Obtener el tipo de vista (tab) seleccionado
    tab = request.GET.get('tab', 'entries')  # Por defecto, mostrar todas las entradas
    
    # Obtener parámetros de filtro
    # Filtro de fecha: por defecto 1 semana
    date_range = request.GET.get('date_range', '7')  # Días por defecto
    
    # Filtro de colecciones: por defecto todas
    collections = request.GET.getlist('collections', ['all'])
    
    # Filtro de favoritos: por defecto incluye todos
    only_favorites = request.GET.get('only_favorites', 'off') == 'on'
    
    # Filtro de borradores: por defecto no incluye borradores
    only_drafts = request.GET.get('include_drafts', 'off') == 'on'
    
    # Obtener todas las colecciones del usuario para el filtro
    user_collections = Collection.objects.filter(user=request.user)
    
    # Construir la consulta base
    entries = Entry.objects.filter(user=request.user)
    
    # Aplicar filtros según la pestaña seleccionada
    if tab == 'favorites':
        entries = entries.filter(status='favorite')
    elif tab == 'drafts':
        entries = entries.filter(status='draft')
    else:  # tab == 'entries' (todas las entradas)
        # Aplicar filtro de favoritos solo si estamos en la pestaña principal
        if only_favorites:
            entries = entries.filter(status='favorite')
        
        # Aplicar filtro de borradores solo si estamos en la pestaña principal
        if only_drafts:
            entries = entries.filter(status='draft')
        else:
            # Si no estamos mostrando solo borradores, excluirlos por defecto
            entries = entries.exclude(status='draft')
    
    # Aplicar filtro de colecciones (en todas las pestañas)
    if collections and collections != ['all']:
        entries = entries.filter(collection__pk__in=collections)
    
    # Aplicar filtro de fecha (en todas las pestañas)
    if date_range and date_range.isdigit():
        days = int(date_range)
        date_from = timezone.now() - timezone.timedelta(days=days)
        entries = entries.filter(created_at__gte=date_from)
    
    # Excluir entradas eliminadas
    entries = entries.exclude(status='deleted')
    
    # Ordenar por fecha de creación (más reciente primero)
    entries = entries.order_by('-created_at')
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(entries, 5)  # 5 entradas por página
    
    try:
        entries_page = paginator.page(page)
    except PageNotAnInteger:
        entries_page = paginator.page(1)
    except EmptyPage:
        entries_page = paginator.page(paginator.num_pages)
    
    # Preparar opciones para el filtro de fecha
    date_range_options = [
        {'value': '1', 'label': 'Último día'},
        {'value': '7', 'label': 'Última semana'},
        {'value': '30', 'label': 'Último mes'},
        {'value': '90', 'label': 'Últimos 3 meses'},
        {'value': '365', 'label': 'Último año'},
        {'value': 'all', 'label': 'Todo el tiempo'}
    ]
    
    # Convertir las colecciones seleccionadas a strings para comparación en la plantilla
    selected_collections = [str(c) for c in collections]
    
    # Formulario para crear una nueva entrada
    if request.method == 'POST':
        # Procesar el formulario
        title = request.POST.get('title')
        content = request.POST.get('content')
        collection_id = request.POST.get('collection')
        status = request.POST.get('status', 'saved')
        visibility = request.POST.get('visibility', 'private')
        entry_image = request.FILES.get('entry_image')
        
        # Validación básica
        form_errors = {}
        
        if not title:
            form_errors['title'] = ['Este campo es obligatorio.']
        
        if not content:
            form_errors['content'] = ['Este campo es obligatorio.']
        
        if not collection_id:
            form_errors['collection'] = ['Debes seleccionar una colección.']
        
        # Si no hay errores, crear la entrada
        if not form_errors:
            try:
                collection = Collection.objects.get(pk=collection_id, user=request.user)
                
                entry = Entry(
                    title=title,
                    content=content,
                    collection=collection,
                    user=request.user,
                    status=status,
                    visibility=visibility
                )
                
                if entry_image:
                    entry.entry_image = entry_image
                
                entry.save()
                
                messages.success(request, 'Entrada creada correctamente.')
                return redirect('profile')
            
            except Collection.DoesNotExist:
                form_errors['collection'] = ['La colección seleccionada no existe.']
        
        # Si hay errores, mostrarlos en el formulario
        context = {
            'form_errors': form_errors,
            'form': {
                'title': {'value': title},
                'content': {'value': content},
                'collection': {'value': collection_id},
                'status': {'value': status},
                'visibility': {'value': visibility}
            }
        }
    else:
        context = {}
    
    # Añadir el resto de variables al contexto
    context.update({
        'tab': tab,
        'entries': entries_page,
        'user_collections': user_collections,
        'date_range': date_range,
        'date_range_options': date_range_options,
        'selected_collections': selected_collections,
        'only_favorites': only_favorites,
        'include_drafts': only_drafts,
        'title': 'Perfil'
    })
    
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    """Vista para editar el perfil del usuario."""
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('profile')
        else:
            # Mostrar errores específicos
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {user_form[field].label}: {error}")
            
            if not profile_form.is_valid():
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {profile_form[field].label}: {error}")
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'core/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Editar Perfil'
    })

@login_required
def change_username(request):
    """Vista para cambiar el nombre de usuario."""
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu nombre de usuario ha sido actualizado correctamente.')
            return redirect('profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ChangeUsernameForm(instance=request.user)
    
    return render(request, 'core/change_username.html', {
        'form': form,
        'title': 'Cambiar Nombre de Usuario'
    })

@login_required
def change_password(request):
    """Vista para cambiar la contraseña del usuario."""
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener la sesión activa después de cambiar la contraseña
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, 'core/change_password.html', {
        'form': form,
        'title': 'Cambiar Contraseña'
    })

class CustomPasswordResetView(PasswordResetView):
    """Vista personalizada para la recuperación de contraseña."""
    template_name = 'core/password_reset.html'
    email_template_name = 'core/password_reset_email.html'
    html_email_template_name = 'core/password_reset_email.html'
    plain_email_template_name = 'core/password_reset_email.txt'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    subject_template_name = 'core/password_reset_subject.txt'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        """Sobreescribir para usar la URL del sitio configurada en settings."""
        self.extra_email_context = {
            'site_url': settings.SITE_URL,
            'site_name': 'Eureka',
            'domain': settings.SITE_URL.replace('http://', '').replace('https://', '').rstrip('/'),
            'protocol': 'https' if settings.SITE_URL.startswith('https') else 'http',
        }
        return super().form_valid(form)

def password_reset_view(request):
    """Vista para la recuperación de contraseña."""
    if request.user.is_authenticated:
        messages.info(request, 'Ya has iniciado sesión.')
        return redirect('home')
    
    return CustomPasswordResetView.as_view()(request)

@login_required
def collection_list(request):
    """Vista para listar todas las colecciones del usuario."""
    collections = Collection.objects.filter(user=request.user)
    return render(request, 'core/collection_list.html', {
        'collections': collections,
        'title': 'Mis Colecciones'
    })

@login_required
def collection_create(request):
    """Vista para crear una nueva colección."""
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.save()
            messages.success(request, 'Colección creada correctamente.')
            return redirect('collection_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {form[field].label}: {error}")
    else:
        form = CollectionForm()
    
    return render(request, 'core/collection_form.html', {
        'form': form,
        'title': 'Crear Colección',
        'button_text': 'Crear'
    })

@login_required
def collection_edit(request, pk):
    """Vista para editar una colección existente."""
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colección actualizada correctamente.')
            return redirect('collection_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {form[field].label}: {error}")
    else:
        form = CollectionForm(instance=collection)
    
    return render(request, 'core/collection_form.html', {
        'form': form,
        'collection': collection,
        'title': 'Editar Colección',
        'button_text': 'Actualizar'
    })

@login_required
def collection_delete(request, pk):
    """Vista para eliminar una colección."""
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Guardar el nombre para el mensaje
        collection_name = collection.name
        collection.delete()
        messages.success(request, f'La colección "{collection_name}" ha sido eliminada correctamente.')
        return redirect('collection_list')
    
    return render(request, 'core/collection_confirm_delete.html', {
        'collection': collection,
        'title': 'Eliminar Colección'
    })

@login_required
def collection_detail(request, pk):
    """Vista para ver el detalle de una colección y sus entradas."""
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    
    # Obtener parámetros de filtro
    # Filtro de fecha: por defecto 1 semana
    date_range = request.GET.get('date_range', '7')  # Días por defecto
    
    # Filtro de colecciones: por defecto la colección actual
    collections = request.GET.getlist('collections', [str(pk)])
    
    # Filtro de favoritos: por defecto incluye todos
    only_favorites = request.GET.get('only_favorites', 'off') == 'on'
    
    # Filtro de borradores: por defecto no incluye borradores
    only_drafts = request.GET.get('include_drafts', 'off') == 'on'
    
    # Obtener todas las colecciones del usuario para el filtro
    user_collections = Collection.objects.filter(user=request.user)
    
    # Construir la consulta base
    entries = Entry.objects.filter(user=request.user)
    
    # Aplicar filtro de colecciones
    if collections and collections != ['all']:
        entries = entries.filter(collection__pk__in=collections)
    
    # Aplicar filtro de fecha
    if date_range and date_range.isdigit():
        days = int(date_range)
        date_from = timezone.now() - timezone.timedelta(days=days)
        entries = entries.filter(created_at__gte=date_from)
    
    # Aplicar filtro de favoritos
    if only_favorites:
        entries = entries.filter(status='favorite')
    
    # Aplicar filtro de borradores
    if only_drafts:
        entries = entries.filter(status='draft')
    else:
        # Si no estamos mostrando solo borradores, excluirlos por defecto
        entries = entries.exclude(status='draft')
    
    # Excluir entradas eliminadas
    entries = entries.exclude(status='deleted')
    
    # Ordenar por fecha de creación (más reciente primero)
    entries = entries.order_by('-created_at')
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(entries, 5)  # 5 entradas por página
    
    try:
        entries_page = paginator.page(page)
    except PageNotAnInteger:
        entries_page = paginator.page(1)
    except EmptyPage:
        entries_page = paginator.page(paginator.num_pages)
    
    # Preparar opciones para el filtro de fecha
    date_range_options = [
        {'value': '1', 'label': 'Último día'},
        {'value': '7', 'label': 'Última semana'},
        {'value': '30', 'label': 'Último mes'},
        {'value': '90', 'label': 'Últimos 3 meses'},
        {'value': '365', 'label': 'Último año'},
        {'value': 'all', 'label': 'Todo el tiempo'}
    ]
    
    # Convertir las colecciones seleccionadas a strings para comparación en la plantilla
    selected_collections = [str(c) for c in collections]
    
    return render(request, 'core/collection_detail.html', {
        'collection': collection,
        'entries': entries_page,
        'user_collections': user_collections,
        'date_range': date_range,
        'date_range_options': date_range_options,
        'selected_collections': selected_collections,
        'only_favorites': only_favorites,
        'include_drafts': only_drafts,
        'title': collection.name
    })

@login_required
def entry_create(request, collection_pk):
    """Vista para crear una nueva entrada en una colección."""
    collection = get_object_or_404(Collection, pk=collection_pk, user=request.user)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.collection = collection
            entry.save()
            messages.success(request, 'Entrada creada correctamente.')
            return redirect('collection_detail', pk=collection.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {form[field].label}: {error}")
    else:
        form = EntryForm(initial={'status': 'saved', 'visibility': 'private'})
    
    return render(request, 'core/entry_form.html', {
        'form': form,
        'collection': collection,
        'title': 'Nueva Entrada',
        'button_text': 'Crear'
    })

@login_required
def entry_edit(request, pk):
    """Vista para editar una entrada existente."""
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada actualizada correctamente.')
            return redirect('collection_detail', pk=entry.collection.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {form[field].label}: {error}")
    else:
        form = EntryForm(instance=entry)
    
    return render(request, 'core/entry_form.html', {
        'form': form,
        'entry': entry,
        'collection': entry.collection,
        'title': 'Editar Entrada',
        'button_text': 'Actualizar'
    })

@login_required
def entry_delete(request, pk):
    """Vista para eliminar una entrada."""
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    collection = entry.collection
    
    if request.method == 'POST':
        entry_title = entry.title
        
        # Eliminar la imagen del almacenamiento si existe
        if entry.entry_image:
            # Guardar la ruta del archivo para eliminarlo
            image_path = entry.entry_image.path
            if os.path.isfile(image_path):
                os.remove(image_path)
        
        entry.delete()
        messages.success(request, f'La entrada "{entry_title}" ha sido eliminada correctamente.')
        return redirect('collection_detail', pk=collection.pk)
    
    return render(request, 'core/entry_confirm_delete.html', {
        'entry': entry,
        'title': 'Eliminar Entrada'
    })

@login_required
def entry_detail(request, pk):
    """Vista para ver el detalle de una entrada."""
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    
    return render(request, 'core/entry_detail.html', {
        'entry': entry,
        'title': entry.title
    })

@login_required
def entry_toggle_favorite(request, pk):
    """Vista para marcar/desmarcar una entrada como favorita."""
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    
    if entry.status == 'favorite':
        entry.status = 'saved'
        messages.success(request, 'Entrada eliminada de favoritos.')
    else:
        entry.status = 'favorite'
        messages.success(request, 'Entrada marcada como favorita.')
    
    entry.save()
    
    # Redirigir a la página anterior o a la colección
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('collection_detail', pk=entry.collection.pk)

@login_required
def entry_toggle_visibility(request, pk):
    """Vista para cambiar la visibilidad de una entrada."""
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    
    if entry.visibility == 'public':
        entry.visibility = 'private'
        messages.success(request, 'Entrada establecida como privada.')
    else:
        entry.visibility = 'public'
        messages.success(request, 'Entrada establecida como pública.')
    
    entry.save()
    
    # Redirigir a la página anterior o a la colección
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('collection_detail', pk=entry.collection.pk)

@login_required
def profile_entry_create(request):
    """Vista para crear una entrada desde el perfil."""
    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            
            # Obtener la colección seleccionada
            collection_id = request.POST.get('collection')
            if collection_id:
                try:
                    collection = Collection.objects.get(pk=collection_id, user=request.user)
                    entry.collection = collection
                except Collection.DoesNotExist:
                    messages.error(request, 'La colección seleccionada no existe o no te pertenece.')
                    return redirect('profile')
            else:
                messages.error(request, 'Debes seleccionar una colección para tu entrada.')
                return redirect('profile')
            
            entry.save()
            messages.success(request, 'Entrada creada con éxito.')
            return redirect('profile')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            
            # Guardar el formulario con errores en la sesión para mostrarlo en la vista de perfil
            request.session['form_data'] = request.POST
            request.session['form_errors'] = form.errors
    
    return redirect('profile')

@login_required
def home_entry_create(request):
    """Vista para crear una entrada desde la página de inicio."""
    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            
            # Obtener la colección seleccionada
            collection_id = request.POST.get('collection')
            if collection_id:
                try:
                    collection = Collection.objects.get(pk=collection_id, user=request.user)
                    entry.collection = collection
                except Collection.DoesNotExist:
                    messages.error(request, 'La colección seleccionada no existe o no te pertenece.')
                    return redirect('home')
            else:
                messages.error(request, 'Debes seleccionar una colección para tu entrada.')
                return redirect('home')
            
            entry.save()
            messages.success(request, 'Entrada creada con éxito.')
            return redirect('home')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            
            # Guardar el formulario con errores en la sesión para mostrarlo en la vista de inicio
            request.session['form_data'] = request.POST
            request.session['form_errors'] = form.errors
    
    return redirect('home')

def terms_view(request):
    """Vista para los términos de servicio."""
    return render(request, 'core/terms.html', {'title': 'Términos de Servicio'})

def privacy_view(request):
    """Vista para la política de privacidad."""
    return render(request, 'core/privacy.html', {'title': 'Política de Privacidad'})
