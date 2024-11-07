from rest_framework import routers

from payment.views import *


router = routers.SimpleRouter()
router.register(r'', PaymentsViewSet, basename='recibos')

urlpatterns = []
urlpatterns += router.urls