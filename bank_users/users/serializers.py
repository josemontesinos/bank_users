from rest_framework import serializers, validators
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user model.
    """
    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'iban',
            'balance',
            'currency',
            'create_ts',
            'update_ts'
        )
        read_only_fields = ('create_ts', 'update_ts')
        extra_kwargs = {
            'password': {'write_only': True},
            'iban': {'required': True}
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['currency'] = instance.get_currency_display()
        return ret

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data=validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance=instance, validated_data=validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

    def validate_iban(self, value):
        if not value:
            raise validators.ValidationError('IBAN is required.')
        return value
