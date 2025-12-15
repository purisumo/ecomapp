from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView 

urlpatterns = [
    path('', RedirectView.as_view(url='/shop/', permanent=False)),  # ← Add this line
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)