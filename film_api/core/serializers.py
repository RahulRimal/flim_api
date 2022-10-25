from dataclasses import fields
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    # def create(self, validated_data):
    #     user = User.objects.create(
    #         username=validated_data['username'], email=validated_data['email'], password=make_password(validated_data['password']))
    #     return user

    def validate_password(self, value: str) -> str:
        return make_password(value)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
