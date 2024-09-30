from rest_framework import routers

from user.views import *


router = routers.SimpleRouter()
router.register(r'items', ClientPayerViewSet, basename='clientsPayer')

urlpatterns = []
urlpatterns += router.urls