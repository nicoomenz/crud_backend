from rest_framework import routers

from payment.views import *


router = routers.SimpleRouter()
router.register(r'precio_historico', PaymentProductViewSet, basename='precio_historico')
router.register(r'', PaymentsViewSet, basename='recibos')


urlpatterns = []
urlpatterns += router.urls