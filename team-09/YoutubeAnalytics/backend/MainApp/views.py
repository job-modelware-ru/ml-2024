import re

import drf_yasg.openapi
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware import csrf
import urllib.parse

import settings.settings
from MainApp.serializers import *
from rest_framework import viewsets, permissions, status


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class IsValidated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    permission_classes = [IsValidated]
    serializer_class = ChannelSerializer


class EmotionViewSet(viewsets.ModelViewSet):
    queryset = Emotion.objects.all()
    permission_classes = [IsValidated]
    serializer_class = EmotionSerializer


class ChannelGroupViewSet(viewsets.ModelViewSet):
    queryset = ChannelGroup.objects.all()
    permission_classes = [IsValidated]
    serializer_class = ChannelGroupSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = ChannelGroup.objects.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = ChannelGroup.objects.filter(user=request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        channel = {k: ChannelSerializer(Channel.objects.get(pk=k)).data for k in data["channel"]}
        data["channel"] = channel
        return Response(data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VideoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsValidated]
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects
    permission_classes = [permissions.AllowAny]
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('video_id', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='id видео для фильтрации',
                              required=True),
            openapi.Parameter('emotion_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id эмоции для фильтрации',
                              required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        video_id = self.request.query_params.get('video_id', None)
        emotion_id = self.request.query_params.get('emotion_id', None)

        if video_id:
            self.queryset = self.queryset.filter(video__yt_id=video_id)
        else:
            raise ParseError("product_category: обязательный параметр")
        if emotion_id:
            self.queryset = self.queryset.filter(emotion__id=emotion_id)

        return super().list(request, *args, **kwargs)


class VideoGroupViewSet(viewsets.ModelViewSet):
    queryset = VideoGroup.objects.all()
    permission_classes = [IsValidated]
    serializer_class = VideoGroupSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = VideoGroup.objects.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = VideoGroup.objects.filter(user=request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        print(data["videos"])
        videos = {k: VideoSerializer(Video.objects.get(pk=k)).data for k in data["videos"]}
        data["videos"] = videos

        return Response(data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    permission_classes = [IsValidated]
    serializer_class = RequestSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = Request.objects.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = Request.objects.filter(user=request.user)
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        data["date_completion"] = None
        data["progress"] = 1

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CalculationResultViewSet(viewsets.ModelViewSet):
    queryset = CalculationResult.objects.all()
    permission_classes = [IsValidated]
    serializer_class = CalculationResultSerializer

    def list(self, request, *args, **kwargs):
        yt_id = request.data.get("yt_id", None)
        self.queryset = CalculationResult.objects.filter(user=request.user)
        if yt_id is not None:
            self.queryset = self.queryset(yt_id=yt_id)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        yt_id = request.data.get("yt_id", None)
        self.queryset = CalculationResult.objects.filter(user=request.user)
        if yt_id is not None:
            self.queryset = self.queryset(yt_id=yt_id)
        return super().retrieve(request, *args, **kwargs)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('refresh_token', openapi.IN_HEADER, type=openapi.TYPE_STRING,
                              description='refresh token cookie',
                              required=True)
        ],
        responses={status.HTTP_200_OK: drf_yasg.openapi.Response('reobtained refresh token', Schema(
            type=TYPE_OBJECT,
            properties={
                'token': Schema(
                    type=TYPE_STRING
                )
            }
        ), {"application/json": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1ODk3MjY2LCJpYXQiOjE3MTU4OTY5NjYsImp0aSI6IjYxZmQxYmY5ODE0YTQ2MDE4NTc0YWI0YzZjNDc2MWRmIiwidXNlcl9pZCI6MX0.dCAjunkoVnElPmttth5zjaf9z3a9FvNMBiuOLltUIIo"}}),
                   403: "This account is not active!!", 404: "Invalid username or password!!"}
    )
    def post(self, request, format=None):
        response = Response(status=status.HTTP_200_OK)

        cookie = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'], None)
        user = None
        if cookie is not None:

            try:
                token = RefreshToken(cookie)
            except TokenError as terror:
                return Response({"Error": str(terror)})
            user = User.objects.get(pk=token.payload['user_id'])
            token.blacklist()
        else:
            return Response({"Error": "No refresh token cookie found!"}, status=status.HTTP_403_FORBIDDEN)

        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=data["refresh"],
                    max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                csrf.get_token(request)
                response.data = {"token": data['access']}

                return response
            else:
                return Response({"No active": "This account is not active!!"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"Invalid": "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={status.HTTP_200_OK: drf_yasg.openapi.Response('successfully authenticated', Schema(
            type=TYPE_OBJECT,
            properties={
                'token': Schema(
                    type=TYPE_STRING
                )
            }
        ), {"application/json": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1ODk3MjY2LCJpYXQiOjE3MTU4OTY5NjYsImp0aSI6IjYxZmQxYmY5ODE0YTQ2MDE4NTc0YWI0YzZjNDc2MWRmIiwidXNlcl9pZCI6MX0.dCAjunkoVnElPmttth5zjaf9z3a9FvNMBiuOLltUIIo"}}),
                   403: "This account is not active!!", 404: "Invalid username or password!!"}
    )
    def post(self, request, format=None):

        data = request.data
        response = Response()
        username = data.get('username', None)
        password = data.get('password', None)
        email = data.get('email', None)

        if username is None and email is not None:
            user = User.objects.get(email=email)
            username = user.username

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=data["refresh"],
                    max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                csrf.get_token(request)
                response.data = {"token": data['access']}

                return response
            else:
                return Response({"No active": "This account is not active!!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Invalid": "Invalid username or password!!"}, status=status.HTTP_400_BAD_REQUEST)


class SignUp(GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: drf_yasg.openapi.Response("Account successfully created", Schema(
            type=TYPE_OBJECT,
            properties={
                'success': Schema(
                    type=TYPE_STRING
                )
            }
        ), {"application/json": {
            "success": "Account successfully created"}}),
                   })
    def post(self, request):
        with transaction.atomic():
            data = request.data
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user = serializer.data

            absurl = 'http://' + get_current_site(request).domain + reverse('email-verify')
            params = {'email': user['email'], 'token': user['token']}
            url = absurl + '?' + urllib.parse.urlencode(params)
            email_body = 'Hi ' + user['username'] + ',\nUse the link below to verify your email \n' + url
            send_mail('Verify your email', email_body, None, [user['email']], False, )

            return Response({"success": "Account successfully created"}, status=status.HTTP_201_CREATED)


class VerifyEmail(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("token", type=openapi.TYPE_STRING, description="user's token", in_=openapi.IN_PATH),
            openapi.Parameter("email", type=openapi.TYPE_STRING, description="email", in_=openapi.IN_PATH)],
        responses={
            status.HTTP_200_OK: drf_yasg.openapi.Response("email successfully verified",
                                                          Schema(
                                                              type=TYPE_OBJECT,
                                                              properties={'success': Schema(type=TYPE_STRING)}
                                                          ), {"application/json": {
                    "success": "email successfully verified"}}),
            status.HTTP_400_BAD_REQUEST: drf_yasg.openapi.Response("error",
                                                                   Schema(
                                                                       type=TYPE_OBJECT,
                                                                       properties={'error': Schema(type=TYPE_STRING)}
                                                                   ), {"application/json": {"error": "Invalid email"}}),
        })
    def get(self, request):
        token = request.GET.get('token')
        email = request.GET.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

        if not token == user.token:
            return Response({'error': 'Invalid token'}, status.HTTP_400_BAD_REQUEST)

        if user.is_verified:
            return Response({'error': 'User already verified'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.is_verified = True
            user.save()

        return Response({'success': 'email successfully verified'}, status=status.HTTP_200_OK)


class SendVerificationLink(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.is_verified:
            return Response({'error': 'User already verified'}, status=status.HTTP_400_BAD_REQUEST)

        absurl = 'https://' + get_current_site(request).domain + reverse('email-verify')
        params = {'email': request.user.email, 'token': request.user.token}
        url = absurl + '?' + urllib.parse.urlencode(params)
        email_body = 'Hi ' + request.user.username + ',\nUse the link below to verify your email \n' + url
        send_mail('Verify your email', email_body, None, [request.user.email], False)

        return Response(status=status.HTTP_200_OK)


def get_youtube_video_id(url):
    video_id = None

    pattern = r"^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"

    match = re.search(pattern, url)
    if match:
        video_id = match.group(7)
    return video_id


class MakeDownloadRequest(GenericAPIView):
    permission_classes = [IsValidated]

    def post(self, request):
        yt_id = request.POST.get('id', None)
        request_type = request.POST.get('request_type', None)

        if yt_id is not None:
            return Response()

        return Response()


class ProfileView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)


class LogoutView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cookie = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'], None)
        if cookie is not None:
            try:
                token = RefreshToken(cookie)
            except TokenError as terror:
                return Response({"Error": str(terror)})
            token.blacklist()
        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={status.HTTP_200_OK: drf_yasg.openapi.Response("Password successfully changed", Schema(
            type=TYPE_OBJECT,
            properties={
                'success': Schema(
                    type=TYPE_STRING
                )
            }
        ), {"application/json": {
            "success": "Password successfully changed"}}),
                   })
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data.get('old_password', None)
        new_password = serializer.validated_data.get('new_password', None)

        user = authenticate(username=request.user.username, password=old_password)

        if user is not None:
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)

        return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)


class AddVideoToGroupView(GenericAPIView):
    permission_classes = [IsValidated]

    @swagger_auto_schema(
        request_body=AddVideoToGroupSerializer,
        responses={status.HTTP_200_OK: drf_yasg.openapi.Response('successfully added', schema=VideoSerializer),
                   status.HTTP_400_BAD_REQUEST: drf_yasg.openapi.Response('invalid data')}
    )
    def post(self, request):
        video_group_id = request.data.get("video_group_id", None)
        video_yt_id = request.data.get("video_yt_id", None)

        if video_yt_id is None:
            return Response({"invalid data": "video_yt_id mustn't be empty"}, status=status.HTTP_400_BAD_REQUEST)
        if video_group_id is None:
            return Response({"invalid data": "video_group_id mustn't be empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(yt_id=video_yt_id)
        except Video.DoesNotExist:
            return Response({"invalid data": f"No video with video_yt_id = {video_yt_id}"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            video_group = VideoGroup.objects.get(pk=video_group_id)
        except VideoGroup.DoesNotExist:
            return Response({"invalid data": f"No video_group with video_group_id = {video_group_id}"},
                            status=status.HTTP_400_BAD_REQUEST)

        video_group.videos.add(video)

        return Response(VideoSerializer(video).data)


class AddChannelToGroupView(GenericAPIView):
    permission_classes = [IsValidated]

    @swagger_auto_schema(
        request_body=AddChannelToGroupSerializer,
        responses={status.HTTP_200_OK: drf_yasg.openapi.Response('successfully added', schema=ChannelSerializer),
                   status.HTTP_400_BAD_REQUEST: drf_yasg.openapi.Response('invalid data')}
    )
    def post(self, request):
        channel_group_id = request.data.get("channel_group_id", None)
        custom_url = request.data.get("custom_url", None)

        if custom_url is None:
            print(1)
            return Response({"invalid data": "custom_url mustn't be empty"}, status=status.HTTP_400_BAD_REQUEST)
        if channel_group_id is None:
            print(2)
            return Response({"invalid data": "channel_group_id mustn't be empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel = Channel.objects.get(custom_url=custom_url)
        except Channel.DoesNotExist:
            print(3)
            return Response({"invalid data": f"No channel with custom_url = {custom_url}"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            channel_group = ChannelGroup.objects.get(pk=channel_group_id)
        except ChannelGroup.DoesNotExist:
            print(4)
            return Response({"invalid data": f"No channel_group with channel_group_id = {channel_group_id}"},
                            status=status.HTTP_400_BAD_REQUEST)

        channel_group.channel.add(channel)

        return Response(ChannelSerializer(channel).data)
