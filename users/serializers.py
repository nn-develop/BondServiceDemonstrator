from rest_framework import serializers
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from bond_service_demonstrator.logger import logger


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields: tuple = ("username", "email", "password")

    def create(self, validated_data: dict[str, str]) -> User:
        """
        Creates a user and generates a token.
        """
        validated_username: str = validated_data["username"]
        validated_email: str = validated_data.get("email", "")

        logger.debug(
            f"Registration started for user '{validated_username}' with email '{validated_email}'."
        )

        try:
            user: User = User.objects.create_user(
                username=validated_username,
                email=validated_email,
                password=validated_data["password"],
            )

            logger.info(f"User '{validated_username}' successfully created.")

            Token.objects.create(user=user)

            logger.debug(f"Token created for user '{validated_username}'.")

            return user

        except IntegrityError as e:
            logger.error(f"Database error during registration: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            raise
