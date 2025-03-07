from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import uuid
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Collection(models.Model):
    """Modelo para las colecciones de escritura de los usuarios."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Colección'
        verbose_name_plural = 'Colecciones'

def get_profile_image_path(instance, filename):
    """Genera una ruta personalizada para la imagen de perfil."""
    # Obtener la extensión del archivo original
    ext = filename.split('.')[-1]
    # Generar un nombre de archivo único basado en el username y un UUID
    filename = f"{instance.user.username}_profile_{uuid.uuid4().hex}.{ext}"
    # Devolver la ruta completa
    return os.path.join('profile_images', filename)

def get_banner_image_path(instance, filename):
    """Genera una ruta personalizada para la imagen de portada."""
    # Obtener la extensión del archivo original
    ext = filename.split('.')[-1]
    # Generar un nombre de archivo único basado en el username y un UUID
    filename = f"{instance.user.username}_banner_{uuid.uuid4().hex}.{ext}"
    # Devolver la ruta completa
    return os.path.join('profile_banners', filename)

def get_entry_image_path(instance, filename):
    """Genera una ruta personalizada para la imagen de la entrada."""
    # Obtener la extensión del archivo original
    ext = filename.split('.')[-1]
    # Generar un nombre de archivo único basado en el username, collection_id, entry_id y un UUID
    filename = f"{instance.user.username}_entry_{instance.collection.id}_{uuid.uuid4().hex}.{ext}"
    # Devolver la ruta completa
    return os.path.join('entry_images', filename)

class Entry(models.Model):
    """Modelo para las entradas de escritura de los usuarios."""
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('saved', 'Guardado'),
        ('favorite', 'Favorito'),
        ('deleted', 'Eliminado'),
    )
    
    VISIBILITY_CHOICES = (
        ('private', 'Privado'),
        ('public', 'Público'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Imagen de la entrada
    entry_image = ProcessedImageField(
        upload_to=get_entry_image_path,
        processors=[ResizeToFit(1200, 800)],  # Redimensionar a máximo 1200x800 px
        format='JPEG',
        options={'quality': 85},  # Calidad de compresión
        blank=True,
        null=True,
        verbose_name='Imagen de la entrada'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Entrada'
        verbose_name_plural = 'Entradas'

class Friendship(models.Model):
    """Modelo para las relaciones de amistad entre usuarios."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"

    class Meta:
        unique_together = ('user', 'friend')
        verbose_name = 'Amistad'
        verbose_name_plural = 'Amistades'

class Profile(models.Model):
    """Modelo para almacenar información adicional del usuario."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biografía')
    
    # Imagen de perfil procesada
    profile_image = ProcessedImageField(
        upload_to=get_profile_image_path,
        processors=[ResizeToFill(300, 300)],  # Redimensionar a 300x300 px
        format='JPEG',
        options={'quality': 85},  # Calidad de compresión
        blank=True,
        null=True,
        verbose_name='Imagen de perfil'
    )
    
    # Imagen de portada procesada
    banner_image = ProcessedImageField(
        upload_to=get_banner_image_path,
        processors=[ResizeToFit(1200, 400)],  # Redimensionar a máximo 1200x400 px
        format='JPEG',
        options={'quality': 85},  # Calidad de compresión
        blank=True,
        null=True,
        verbose_name='Imagen de portada'
    )
    
    # Versión en miniatura de la imagen de perfil para usar en avatares
    profile_thumbnail = ProcessedImageField(
        upload_to='profile_thumbnails',
        processors=[ResizeToFill(100, 100)],  # Tamaño para avatares pequeños
        format='JPEG',
        options={'quality': 80},
        blank=True,
        null=True,
        verbose_name='Miniatura de perfil'
    )
    
    website = models.URLField(max_length=200, blank=True, verbose_name='Sitio web')
    location = models.CharField(max_length=100, blank=True, verbose_name='Ubicación')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    def __str__(self):
        return f'Perfil de {self.user.username}'
    
    def save(self, *args, **kwargs):
        """Sobreescribir el método save para generar la miniatura automáticamente."""
        # Primero guardamos el modelo para procesar las imágenes
        super().save(*args, **kwargs)
        
        # Si hay una imagen de perfil, generamos la miniatura
        if self.profile_image and not self.profile_thumbnail:
            # Abrir la imagen original
            img = Image.open(self.profile_image.path)
            
            # Crear una miniatura
            img.thumbnail((100, 100))
            
            # Guardar la miniatura
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=80)
            thumb_filename = f"{self.user.username}_thumbnail_{uuid.uuid4().hex}.jpg"
            
            # Asignar la miniatura al campo correspondiente
            self.profile_thumbnail.save(
                thumb_filename,
                ContentFile(thumb_io.getvalue()),
                save=False
            )
            
            # Guardar el modelo nuevamente
            super().save(update_fields=['profile_thumbnail'])
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear un perfil cuando se crea un usuario."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar el perfil cuando se guarda un usuario."""
    instance.profile.save()
