from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields: tuple = ("username", "email", "password")

    def create(self, validated_data):
        # Create user and generate token
        user: User = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        # Create token for the newly registered user
        Token.objects.create(user=user)
        return user
