from django.contrib.auth.hashers import make_password

from MainApp.models import *
from rest_framework import serializers


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'


class ChannelGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelGroup
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emotion
        fields = '__all__'


class VideoGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoGroup
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'


class CalculationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculationResult
        fields = '__all__'


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    token = serializers.CharField(read_only=True)

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password', 'token']
        read_only_fields = ['id']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'is_verified', 'is_staff', 'is_active', 'date_joined']


class AddVideoToGroupSerializer(serializers.Serializer):
    video_group_id = serializers.IntegerField()
    video_yt_id = serializers.CharField()


class AddChannelToGroupSerializer(serializers.Serializer):
    channel_group_id = serializers.IntegerField()
    custom_url = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
