from rest_framework import routers

from user.views import *


router = routers.SimpleRouter()
router.register(r'', ClientPayerViewSet, basename='clientsPayer')

urlpatterns = []
urlpatterns += router.urls