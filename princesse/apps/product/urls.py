from rest_framework import routers

from product.views import *


router = routers.SimpleRouter()
router.register(r'categorias', CategoriasViewSet, basename='categorias')
router.register(r'marcas', MarcasViewSet, basename='marcas')
router.register(r'colores', ColoresViewSet, basename='colores')
router.register(r'talles', TallesViewSet, basename='talles')
router.register(r'', ProductosViewSet, basename='productos')

urlpatterns = []
urlpatterns += router.urls