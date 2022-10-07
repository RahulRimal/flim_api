from dataclasses import field, fields
from rest_framework import serializers
from django.db import transaction


from .models import Cart, CartItem, Category, Customer, Equipment, EquipmentImage, EquipmentPrice, Order, OrderItem, TechnicalSpecification


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


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
    category = CategorySerializer()
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
    category = CategorySerializer()

    class Meta:
        model = Equipment
        fields = ['id', 'name',
                  'inventory', 'price', 'category', 'company', 'featured_image']


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


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'full_payment_status',
                  'booking_payment_status', 'placed_at']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['full_payment_status', 'booking_payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

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
        order = Order.objects.create(customer=customer)
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
