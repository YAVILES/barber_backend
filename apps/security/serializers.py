from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Value
from django.utils.translation import ugettext_lazy as _
from django_restql.mixins import DynamicFieldsMixin
from drf_extra_fields import geo_fields
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.security.models import User, PhotoUser


class RoleDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = serializers.ALL_FIELDS


class RoleUserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class DefaultPhotoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoUser
        fields = serializers.ALL_FIELDS


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    email = serializers.EmailField(required=False)
    last_name = serializers.CharField(max_length=255, required=False)
    photo = serializers.ImageField(required=False)

    # Validate password
    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                raise serializers.ValidationError(detail={"error": error.messages})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        photo = validated_data.pop('photo')
        email = validated_data.get('email')
        validated_data['email'] = str(email).lower()
        try:
            with transaction.atomic():
                user = super(UserCreateSerializer, self).create(validated_data)
                if password:
                    user.set_password(password)
                    user.save(update_fields=['password'])

                if photo:
                    photo_user = PhotoUser.objects.create(
                        user_id=user.id,
                        photo=photo
                    )
                    user.current_photo_id = photo_user.id
                    print(user.current_photo_id)
                    user.save(update_fields=["current_photo_id"])
                   # send_email.delay('Clave Temporal B2B', password, [email])
        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        return validated_data

    def update(self, instance, validated_data):
        photo = validated_data.pop('photo')
        email = validated_data.get('email')
        validated_data['email'] = str(email).lower()
        try:
            with transaction.atomic():
                if photo:
                    photo_user = PhotoUser.objects.create(
                        user_id=instance.id,
                        photo=photo
                    )
                    instance.current_photo_id = photo_user.id
                    user = super(UserCreateSerializer, self).update(instance, validated_data)

        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        return instance

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'name', 'last_name', 'full_name', 'direction', 'phone',
                  'point', 'is_superuser', 'groups', 'info', 'is_barber', 'about', 'photo',)


class UserDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    groups = RoleUserSerializer(many=True, read_only=True)
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    photo = serializers.SerializerMethodField(required=False)
    current_photo = DefaultPhotoUserSerializer(read_only=True)

    def get_photo(self, obj: 'User'):
        if obj.current_photo and hasattr(obj.current_photo.photo, 'url'):
            image_url = obj.current_photo.photo.url
            return image_url
        else:
            return None

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'name', 'last_name', 'full_name', 'direction', 'phone',
                  'point', 'is_superuser', 'groups', 'status', 'status_display', 'info', 'created', 'photo',
                  'current_photo', 'is_barber', 'about',)


class UserSimpleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    photo = serializers.SerializerMethodField(required=False)
    current_photo = DefaultPhotoUserSerializer(read_only=True)

    def get_photo(self, obj: 'User'):
        if obj.current_photo and hasattr(obj.current_photo.photo, 'url'):
            image_url = obj.current_photo.photo.url
            return image_url
        else:
            return None

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'last_name', 'full_name', 'direction', 'phone', 'point',
                  'is_superuser', 'status', 'status_display', 'info', 'created', 'is_barber', 'about', 'photo',
                  'current_photo')


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=255, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        email = validated_data.get('email')
        email = str(email).lower()
        password = validated_data.get('password')
        try:
            password_validation.validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            raise serializers.ValidationError(detail={"error": _('email invalid')})

        user.set_password(password)
        user.save(update_fields=['password'])
        return {'password': '', 'email': email}

    class Meta:
        fields = ('email', 'password',)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        super().validate(attrs)
        refresh = self.get_token(self.user)

        return {
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'jwt_id': self.user.jwt_id,
            'info': self.user.info,
            'is_barber': self.user.is_barber,
            'danger': None,
            'warn': [],
            'name': self.user.full_name,
            "is_superuser": self.user.is_superuser,
        }



