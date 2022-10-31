from dataclasses import field, fields
from enum import unique
from rest_framework import serializers
from django.db import transaction

from rest_framework.settings import import_from_string


from .models import Address, BillingInfo, Cart, CartItem, Category, Customer, Equipment, EquipmentImage, EquipmentPrice, Order, OrderItem, TechnicalSpecification


class SimpleCategorySerializer(serializers.ModelSerializer):

    # equipments_count = serializers.IntegerField(read_only=True)
    # companies = serializers.SerializerMethodField(
    #     method_name='get_equipment_companies')

    class Meta:
        model = Category
        fields = ['id', 'name']


class EquipmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentImage
        fields = ['image']


class EquipmentPriceSerializer(serializers.ModelSerializer):
    _1 = serializers.DecimalField(
        max_digits=8, decimal_places=2, source='price_1_day')
    _2_4 = serializers.DecimalField(
        max_digits=8, decimal_places=2, source='price_2_to_4_days')
    _5_7 = serializers.DecimalField(
        max_digits=8, decimal_places=2, source='price_5_to_7_days')
    _8_more = serializers.DecimalField(
        max_digits=8, decimal_places=2, source='price_8_and_more_days')

    class Meta:
        model = EquipmentPrice
        fields = ['_1', '_2_4',
                  '_5_7', '_8_more']
        # fields = ['price_1_day', 'price_2_to_4_days',
        #           'price_5_to_7_days', 'price_8_and_more_days']


class TechnicalSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalSpecification
        fields = ['specification']


class EquipmentSerializer(serializers.ModelSerializer):

    # equipmentimage_set = EquipmentImageSerializer(many=True)
    images = EquipmentImageSerializer(many=True)
    price = EquipmentPriceSerializer()
    category = SimpleCategorySerializer()
    # technicalspecification_set = TechnicalSpecificationSerializer(many=True)
    technical_specification = TechnicalSpecificationSerializer(
        many=True, source='technicalspecification_set')

    class Meta:
        model = Equipment
        # fields = ['id', 'name', 'slug', 'description',
        #           'inventory', 'category', 'company', 'featured_image', 'equipmentimage_set']
        fields = ['id', 'name', 'slug', 'description', 'technical_specification',
                  'inventory', 'price', 'category', 'company', 'featured_image', 'images']


class SimpleEquipmentSerializer(serializers.ModelSerializer):
    price = EquipmentPriceSerializer()
    category = SimpleCategorySerializer()

    class Meta:
        model = Equipment
        fields = ['id', 'name', 'slug', 'description',
                  'inventory', 'price', 'category', 'company', 'featured_image']


class CategorySerializer(serializers.ModelSerializer):

    equipments_count = serializers.IntegerField(read_only=True)
    # company = serializers.CharField()
    companies = serializers.SerializerMethodField(
        method_name='get_equipment_companies')
    featured_equipment = SimpleEquipmentSerializer()

    class Meta:
        model = Category
        fields = ['id', 'name', 'equipments_count',
                  'featured_equipment', 'companies']

    def get_equipment_companies(self, obj):
        companies = []
        equips = Equipment.objects.filter(category_id=obj.id).all()
        if equips:
            for x in equips:
                if x.company:
                    companies.append(x.company)

        companies = list(set(companies))
        return companies


class CartItemSerializer(serializers.ModelSerializer):
    equipment = SimpleEquipmentSerializer()

    class Meta:
        fields = ['id', 'equipment', 'quantity', 'tenure', 'location']
        model = CartItem


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        fields = ['id', 'items']
        model = Cart


class AddCartItemSerializer(serializers.ModelSerializer):
    equipment_id = serializers.IntegerField()

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        equipment_id = self.validated_data['equipment_id']
        location = self.validated_data['location']
        tenure = self.validated_data['tenure']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, equipment_id=equipment_id, location=location, tenure=tenure)
            cart_item.quantity += self.validated_data['quantity']

            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        fields = ['equipment_id', 'quantity', 'location', 'tenure']
        model = CartItem


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity', 'tenure', 'location']


class OrderItemSerializer(serializers.ModelSerializer):
    equipment = SimpleEquipmentSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'equipment', 'quantity', 'location', 'tenure']


class BillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingInfo
        fields = ['first_name', 'last_name',
                  'phone', 'email', 'convenient_location']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    billing_info = BillingInfoSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'full_payment_status',
                  'booking_payment_status', 'billing_info', 'placed_at']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['full_payment_status', 'booking_payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    billing_info = BillingInfoSerializer()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            (customer, created) = Customer.objects.get_or_create(
                user_id=self.context['user_id'])
        billing_info = BillingInfo.objects.create(
            ** self.validated_data['billing_info'])
        order = Order.objects.create(
            customer=customer, billing_info=billing_info)
        cart_items = CartItem.objects.select_related(
            'equipment').filter(cart_id=cart_id)
        order_items = [
            OrderItem(
                order=order,
                equipment=item.equipment,
                quantity=item.quantity,
                tenure=item.tenure,
                location=item.location,
            ) for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        Cart.objects.filter(pk=cart_id).delete()

        # order_created.send_robust(self.__class__, order=order)

        return order


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['city', 'street', 'zipcode']


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email', 'phone', 'address', 'membership']
