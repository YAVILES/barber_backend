from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from apps.core.models import HairCut
from apps.core.serializers import HairCutDefaultSerializer


class HairCutViewSet(ModelViewSet):
    queryset = HairCut.objects.all()
    serializer_class = HairCutDefaultSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['description', 'price', 'minutes']

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
