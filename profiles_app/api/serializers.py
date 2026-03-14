from rest_framework import serializers
from profiles_app.models import Profile
from auth_app.models import User


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)
    email = serializers.CharField(source='user.email')
    user = serializers.PrimaryKeyRelatedField(source='user.id', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = (
            'user',
            'username',
            'email',
            'first_name',
            'last_name',
            'type',
            'location',
            'tel',
            'description',
            'working_hours',
            'file',
            'created_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        string_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        
        for field in string_fields:
            if data.get(field) is None:
                data[field] = ""
        
        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update user fields
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.save()

        # Update profile fields
        instance.location = validated_data.get('location', instance.location)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        instance.file = validated_data.get('file', instance.file)
        instance.save()

        return instance