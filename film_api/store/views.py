import imp
from urllib import request
from django.shortcuts import render

from django.db.models.aggregates import Count
from django.db.models import F, Q

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.response import Response

from store.filters import EquipmentFilter
from store.pagination import DefaultPagination

from .permissions import IsAdminOrReadOnly, ReadOnly
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CategorySerializer, CreateOrderSerializer, EquipmentSerializer, OrderSerializer, SimpleEquipmentSerializer, UpdateCartItemSerializer, UpdateOrderSerializer, CustomerSerializer

from .models import Cart, CartItem, Category, Customer, Equipment, Order

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin


# Create your views here.


class EquipmentViewSet(ModelViewSet):
    # print(Equipment._meta.get_fields() )
    queryset = Equipment.objects.prefetch_related(
        'images', 'price') .all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EquipmentFilter
    pagination_class = DefaultPagination
    search_fields = ['name', 'description']
    ordering_fields = ['last_update']

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleEquipmentSerializer
        return EquipmentSerializer

    permission_classes = [ReadOnly]


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(
        equipments_count=Count('equipment')).all()

    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Equipment.objects.filter(category_id=kwargs['pk']):
            return Response({'error': 'Category cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):

    # def get_queryset(self):
    #     if (self.request.user.is_superuser):
    #         return Cart.objects.prefetch_related('items__equipment').all()
    #     return Cart.objects.filter()

    queryset = Cart.objects.prefetch_related('items__equipment').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):

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


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if (user.is_staff):
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id=user.id)

        return Order.objects.filter(customer_id=customer_id)


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
