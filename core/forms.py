from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm as DjangoPasswordResetForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import password_validation
from .models import Profile, Collection, Entry

class UserRegistrationForm(UserCreationForm):
    """Formulario personalizado para el registro de usuarios."""
    
    first_name = forms.CharField(
        label='Nombre',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input pl-14',
            'placeholder': 'Ingresa tu nombre'
        })
    )
    
    last_name = forms.CharField(
        label='Apellidos',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input pl-14',
            'placeholder': 'Ingresa tus apellidos'
        })
    )
    
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input pl-14',
            'placeholder': 'Ingresa tu correo electrónico'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalización de los campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-input pl-14',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input pl-14',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input pl-14',
            'placeholder': 'Confirmar contraseña'
        })
        
        # Etiquetas personalizadas
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        
        # Mensajes de ayuda personalizados
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'
        self.fields['password1'].help_text = 'Tu contraseña debe tener al menos 8 caracteres y no puede ser demasiado común.'
        self.fields['password2'].help_text = 'Ingresa la misma contraseña que antes, para verificación.'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo electrónico.')
        return email

class UserLoginForm(AuthenticationForm):
    """Formulario personalizado para el inicio de sesión de usuarios."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalización de los campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-input pl-14',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input pl-14',
            'placeholder': 'Contraseña'
        })
        
        # Etiquetas personalizadas
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password'].label = 'Contraseña'

class PasswordResetForm(DjangoPasswordResetForm):
    """Formulario personalizado para la recuperación de contraseña."""
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Personalización del campo email
        self.fields['email'].widget.attrs.update({
            'class': 'form-input pl-14',
            'placeholder': 'Ingresa tu correo electrónico'
        })
        self.fields['email'].label = 'Correo electrónico'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificar si el correo existe en la base de datos
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No existe ninguna cuenta con este correo electrónico.')
        return email 

class UserProfileForm(forms.ModelForm):
    """Formulario para editar la información básica del usuario."""
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'placeholder': 'Apellido'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full pl-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.instance.username
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email

class ProfileForm(forms.ModelForm):
    """Formulario para editar la información adicional del perfil."""
    bio = forms.CharField(
        max_length=500, 
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent', 
            'placeholder': 'Cuéntanos sobre ti...', 
            'rows': 4
        })
    )
    website = forms.URLField(
        max_length=200, 
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full pl-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'placeholder': 'https://ejemplo.com'
        })
    )
    location = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'placeholder': 'Ciudad, País'
        })
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full pl-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent', 
            'type': 'date'
        })
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full py-2 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'accept': 'image/*'
        })
    )
    banner_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full py-2 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'accept': 'image/*'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['bio', 'website', 'location', 'birth_date', 'profile_image', 'banner_image']
        
    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise forms.ValidationError('La imagen no debe exceder 5MB.')
        return image
        
    def clean_banner_image(self):
        image = self.cleaned_data.get('banner_image')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise forms.ValidationError('La imagen de portada no debe exceder 5MB.')
        return image

class ChangeUsernameForm(forms.ModelForm):
    """Formulario para cambiar el nombre de usuario."""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-eureka-orange focus:border-transparent',
            'placeholder': 'Nuevo nombre de usuario'
        })
    )
    
    class Meta:
        model = User
        fields = ['username']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

class ChangePasswordForm(PasswordChangeForm):
    """Formulario para cambiar la contraseña del usuario."""
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'})
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}),
        help_text=password_validation.password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'})
    )

class CollectionForm(forms.ModelForm):
    """Formulario para crear y editar colecciones."""
    class Meta:
        model = Collection
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la colección',
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción (opcional)',
                'rows': 3
            })
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción'
        }
        help_texts = {
            'name': 'Nombre de tu colección (máximo 100 caracteres)',
            'description': 'Una breve descripción de tu colección (opcional)'
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('El nombre de la colección es obligatorio.')
        return name 

class EntryForm(forms.ModelForm):
    """Formulario para crear y editar entradas."""
    class Meta:
        model = Entry
        fields = ['title', 'content', 'visibility', 'status', 'entry_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la entrada',
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '¿Qué estás pensando?',
                'rows': 5
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'entry_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'title': 'Título',
            'content': 'Contenido',
            'visibility': 'Visibilidad',
            'status': 'Estado',
            'entry_image': 'Imagen'
        }
        help_texts = {
            'title': 'Título de tu entrada (máximo 200 caracteres)',
            'content': 'Escribe aquí tus pensamientos, ideas o conocimientos',
            'visibility': 'Elige quién puede ver esta entrada',
            'status': 'Establece el estado de tu entrada',
            'entry_image': 'Añade una imagen a tu entrada (opcional)'
        }
        
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('El título de la entrada es obligatorio.')
        return title
        
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError('El contenido de la entrada es obligatorio.')
        return content
        
    def clean_entry_image(self):
        image = self.cleaned_data.get('entry_image')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise forms.ValidationError('La imagen no debe exceder 5MB.')
        return image 