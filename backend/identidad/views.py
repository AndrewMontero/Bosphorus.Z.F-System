from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, UsuarioSerializer

RUTA_REFRESCO = "/api/auth/refrescar/"


def _guardar_cookies(response, refresh):
    """
    httponly: JavaScript no lo ve.
    secure: solo por HTTPS (se relaja en desarrollo local, que va por http).
    samesite Lax: no se manda en peticiones desde otros sitios -> anti CSRF.
    """
    seguro = not settings.DEBUG
    response.set_cookie(
        settings.JWT_COOKIE_ACCESS,
        str(refresh.access_token),
        httponly=True,
        secure=seguro,
        samesite="Lax",
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
    )
    # La cookie de refresco solo viaja al endpoint que la necesita.
    response.set_cookie(
        settings.JWT_COOKIE_REFRESH,
        str(refresh),
        httponly=True,
        secure=seguro,
        samesite="Lax",
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path=RUTA_REFRESCO,
    )
    return response


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data["usuario"]

        refresh = RefreshToken.for_user(usuario)
        respuesta = Response(UsuarioSerializer(usuario).data, status=status.HTTP_200_OK)
        return _guardar_cookies(respuesta, refresh)


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        respuesta = Response(status=status.HTTP_204_NO_CONTENT)
        respuesta.delete_cookie(settings.JWT_COOKIE_ACCESS)
        respuesta.delete_cookie(settings.JWT_COOKIE_REFRESH, path=RUTA_REFRESCO)
        return respuesta


class RefrescarView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token = request.COOKIES.get(settings.JWT_COOKIE_REFRESH)
        if not token:
            return Response(
                {"detalle": "No hay sesión que refrescar."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            refresh = RefreshToken(token)
        except TokenError:
            return Response(
                {"detalle": "La sesión expiró. Volvé a iniciar sesión."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        respuesta = Response(status=status.HTTP_204_NO_CONTENT)
        respuesta.set_cookie(
            settings.JWT_COOKIE_ACCESS,
            str(refresh.access_token),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        )
        return respuesta


class YoView(APIView):
    """
    Quien soy, que puedo hacer y donde entro. El frontend arma el menu
    con esto -- por eso los permisos vienen explicitos.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)
