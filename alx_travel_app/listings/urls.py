from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from listings import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'listings', views.ListingViewSet)
router.register(r'bookings', views.BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('bookings/confirm/', views.confirm, name='confirm'),
    path('payments/webhook/', views.chapa_webhook, name='chappa-webhook'),
]