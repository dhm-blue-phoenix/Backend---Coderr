# Third-party
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

# Local
from auth_app.models import User

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializes user login data and validates credentials.
    """

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, including all user details.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "type")


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializes registration data, validates password confirmation, and creates a new user.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "repeated_password", "type")
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords must match."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            type=validated_data.get("type", "customer"),
        )
        return user