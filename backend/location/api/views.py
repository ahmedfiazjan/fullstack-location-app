from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as django_filters
from .serializers import CountrySerializer, StateSerializer, CitySerializer, LocationSerializer
from location.models import Country, State, City, Location
from rest_framework.response import Response
from django.db import models

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class LocationFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name='city__name', lookup_expr='icontains')
    state = django_filters.CharFilter(field_name='state__name', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country__name', lookup_expr='icontains')
    zip_code = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Location
        fields = ['city', 'state', 'country', 'zip_code']

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend
    ]
    search_fields = ['name', 'alpha2', 'alpha3']
    ordering_fields = ['name', 'alpha2', 'alpha3']
    ordering = ['name']

    def get_queryset(self):
        queryset = Country.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(alpha2__icontains=search) |
                models.Q(alpha3__icontains=search)
            )
        return queryset

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend
    ]
    search_fields = ['name', 'abbreviation', 'country__name']
    ordering_fields = ['name', 'abbreviation']
    ordering = ['name']
    filterset_fields = ['country']

    def get_queryset(self):
        queryset = State.objects.select_related('country')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(abbreviation__icontains=search) |
                models.Q(country__name__icontains=search)
            )
        return queryset

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, django_filters.DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_fields = ['state', 'state__country']

    def get_queryset(self):
        queryset = City.objects.select_related('state', 'state__country')
        
        # Get query parameters
        search = self.request.query_params.get('search', None)
        state_id = self.request.query_params.get('state', None)
        
        # Apply state filter if provided
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        
        # Apply search with prioritization
        if search:
            search = search.lower()
            # Split into terms for multi-word search
            search_terms = search.split()
            
            # Create different priority levels using Q objects
            exact_matches = models.Q()
            starts_with_matches = models.Q()
            contains_matches = models.Q()
            
            for term in search_terms:
                # Exact matches (highest priority)
                exact_matches |= models.Q(name__iexact=term)
                
                # Starts with matches (medium priority)
                starts_with_matches |= models.Q(name__istartswith=term)
                
                # Contains matches (lowest priority)
                contains_matches |= models.Q(name__icontains=term)
            
            # Combine all matches with Case/When for proper ordering
            from django.db.models import Case, When, Value, IntegerField
            
            queryset = queryset.annotate(
                match_rank=Case(
                    When(exact_matches, then=Value(3)),
                    When(starts_with_matches, then=Value(2)),
                    When(contains_matches, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).filter(match_rank__gt=0).order_by('-match_rank', 'name')
        
        # Debug logging
        print(f"Search terms: {search if search else 'None'}")
        print(f"State ID: {state_id if state_id else 'None'}")
        print(f"SQL Query: {queryset.query}")
        print(f"Result count: {queryset.count()}")
        
        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        # Add debug info about request parameters
        print(f"Request parameters: {request.query_params}")
        
        response = super().list(request, *args, **kwargs)
        
        # Add debug info about response
        print(f"Response data count: {len(response.data['results'] if 'results' in response.data else [])}")
        
        return response

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend
    ]
    search_fields = [
        'zip_code',
        'city__name',
        'state__name',
        'country__name'
    ]
    ordering_fields = ['zip_code', 'city__name', 'state__name']
    ordering = ['zip_code']
    filterset_class = LocationFilter

    def get_queryset(self):
        queryset = Location.objects.select_related('city', 'state', 'country')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(zip_code__icontains=search) |
                models.Q(city__name__icontains=search) |
                models.Q(state__name__icontains=search) |
                models.Q(country__name__icontains=search)
            )
        return queryset

class ZipCodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend
    ]
    search_fields = [
        'zip_code',
        'city__name',
        'state__name',
        'country__name'
    ]
    ordering_fields = ['zip_code', 'city__name']
    ordering = ['zip_code']
    filterset_class = LocationFilter

    def get_queryset(self):
        queryset = Location.objects.select_related('city', 'state', 'country')
        
        # Get query parameters
        city_param = self.request.query_params.get('city', None)
        search = self.request.query_params.get('search', None)
        
        # Apply filters
        if city_param:
            try:
                # First try to interpret as a city ID from zipcodes table
                city_id = int(city_param)
                # Look up the city name from the zipcodes table
                city_name = Location.objects.filter(city_id=city_id).values_list('city__name', flat=True).first()
                
                if city_name:
                    queryset = queryset.filter(city__name=city_name)
                else:
                    # If city_id doesn't exist in zipcodes, return empty queryset
                    queryset = queryset.none()
                
                # Debug logging
                print(f"Filtering by city_id: {city_id}, found city_name: {city_name}")
                print(f"SQL Query: {queryset.query}")
                print(f"Result count: {queryset.count()}")
            except ValueError:
                # If not a number, treat as a city name
                queryset = queryset.filter(
                    models.Q(city__name__icontains=city_param)
                )
            
        if search:
            queryset = queryset.filter(
                models.Q(zip_code__icontains=search) |
                models.Q(city__name__icontains=search) |
                models.Q(state__name__icontains=search) |
                models.Q(country__name__icontains=search)
            )
        
        # Additional debug info
        print(f"Final SQL Query: {queryset.query}")
        print(f"Final Result count: {queryset.count()}")
        
        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        # Add debug info about request parameters
        print(f"Request parameters: {request.query_params}")
        
        response = super().list(request, *args, **kwargs)
        
        # Add debug info about response
        print(f"Response data count: {len(response.data['results'] if 'results' in response.data else [])}")
        
        return response