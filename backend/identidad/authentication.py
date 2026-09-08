from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTDesdeCookie(JWTAuthentication):
    """
    Lee el token de una cookie httpOnly en vez del encabezado Authorization.

    El token nunca queda al alcance de JavaScript, asi que un XSS no puede
    robarlo. Es el mismo patron del ADR-006 de ARDI.
    """

    def authenticate(self, request):
        token = request.COOKIES.get(settings.JWT_COOKIE_ACCESS)
        if not token:
            return None
        validado = self.get_validated_token(token)
        return self.get_user(validado), validado
