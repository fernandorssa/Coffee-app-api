from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coffee import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)

app_name = 'coffee'

urlpatterns = [
    path('', include(router.urls))
]
