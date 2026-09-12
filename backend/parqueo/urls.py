from rest_framework.routers import DefaultRouter

from .views import IngresoViewSet, TarifaViewSet, TipoVehiculoViewSet

router = DefaultRouter()
router.register("tipos-vehiculo", TipoVehiculoViewSet, basename="tipo-vehiculo")
router.register("tarifas", TarifaViewSet, basename="tarifa")
router.register("ingresos", IngresoViewSet, basename="ingreso")

urlpatterns = router.urls
