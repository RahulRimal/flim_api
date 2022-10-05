from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .permissions import ReadOnly

from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, EquipmentSerializer, UpdateCartItemSerializer

from .models import Cart, CartItem, Equipment

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin


# Create your views here.


class EquipmentViewSet(ModelViewSet):
    # print(Equipment._meta.get_fields() )
    queryset = Equipment.objects.prefetch_related(
        'images', 'price') .all()
    serializer_class = EquipmentSerializer

    permission_classes = [ReadOnly]


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__equipment').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    # serializer_class = CartItemSerializer

    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {
            'cart_id': self.kwargs['cart_pk']
        }

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('equipment__price')
