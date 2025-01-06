from django.contrib import admin
from django.urls import include, path
from apps.user.views import UserLoginView, UserLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recibos/', include('payment.urls')),
    path('productos/', include('product.urls')),
    path('usuarios/', include('user.urls')),
    path('login/', UserLoginView.as_view()),
    path('logout/', UserLogoutView.as_view()),
]
