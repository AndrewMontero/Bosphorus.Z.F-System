from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UsuarioManager(BaseUserManager):
    """
    Reemplaza al manager por defecto de Django porque nuestro Usuario
    no tiene "username" -- el correo es el identificador de acceso.
    """

    use_in_migrations = True

    def _crear_usuario(self, email, password, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un correo electronico.")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._crear_usuario(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._crear_usuario(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Identidad de una persona en el sistema.

    is_active es el "activo" del que hablamos para la politica de RRHH:
    un usuario nunca se borra, se desactiva -- su historial de acciones
    en el resto del sistema debe seguir siendo consultable.

    is_staff / is_superuser son la llave de Django al panel /admin/, una
    cosa tecnica para desarrollo y soporte. NO son el "superadministrador
    de negocio" del que hablamos (el que asigna roles y ambitos a otros
    usuarios): ese es un Rol de la app "autorizacion", que se agrega en
    el siguiente paso.
    """

    username = None
    email = models.EmailField("correo electronico", unique=True)
    nombre_completo = models.CharField("nombre completo", max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.email
