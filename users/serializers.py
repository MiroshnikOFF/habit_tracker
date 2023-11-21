from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ['pk', 'email', 'last_name', 'first_name', 'password']

    def create(self, validated_data):
        """Создает пользователя и устанавливает ему пароль"""

        instance = super().create(validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Обновляет пользователя входящими данными и устанавливает ему пароль"""

        instance = super().update(instance, validated_data)
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
