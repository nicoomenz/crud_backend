from django.contrib import admin
from django.urls import include, path
from apps.user.views import CustomTokenObtainPairView, UserLoginView, UserLogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('recibos/', include('payment.urls')),
        path('productos/', include('product.urls')),
        path('usuarios/', include('user.urls')),
        path('login/', UserLoginView.as_view()),
        path('logout/', UserLogoutView.as_view()),
        path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),
]