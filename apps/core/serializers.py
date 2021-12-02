from django.db import transaction
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from apps.core.models import HairCut, HairCutImage


class HairCutDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    images_display = serializers.SerializerMethodField(required=False, read_only=True)
    images = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        required=False, write_only=True
    )

    def get_images_display(self, obj: 'Product'):
        images = []
        for img in obj.images.all():
            if img.image and hasattr(img.image, 'url'):
                image_url = img.image.url
                images.append(image_url)
        return images

    def create(self, validated_data):
        try:
            with transaction.atomic():
                images = validated_data.pop('images', None)
                haircut = super(HairCutDefaultSerializer, self).create(validated_data)

                if images:
                    for img in images:
                        HairCutImage.objects.create(image=img, haircut_id=haircut.id)

        except ValueError as e:
            raise serializers.ValidationError(detail={"error": e})
        return haircut

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                images = validated_data.pop('images', None)

                haircut = super(HairCutDefaultSerializer, self).update(instance, validated_data)

                if images:
                    HairCutImage.objects.filter(haircut_id=haircut.id).delete()
                    for img in images:
                        HairCutImage.objects.create(image=img, haircut_id=haircut.id)

        except ValueError as e:
            raise serializers.ValidationError(detail={"error": e})
        return instance

    class Meta:
        model = HairCut
        fields = serializers.ALL_FIELDS
