from rest_framework import routers

from apps.core.views import HairCutViewSet

router = routers.SimpleRouter()
router.register(r'haircut', HairCutViewSet)

urlpatterns = [
]

urlpatterns += router.urls
