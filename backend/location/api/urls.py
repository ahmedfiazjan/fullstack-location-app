from django.urls import path
from .views import CountryViewSet, StateViewSet, CityViewSet, LocationViewSet, ZipCodeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'states', StateViewSet)
router.register(r'cities', CityViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'zipcodes', ZipCodeViewSet)

urlpatterns = router.urls