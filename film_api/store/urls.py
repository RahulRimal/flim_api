
from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()

router.register('equipments', views.EquipmentViewSet)
router.register('carts', views.CartViewSet)
router.register('orders', views.OrderViewSet, basename='order')
router.register('customers', views.CustomerViewSet)

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + carts_router.urls
