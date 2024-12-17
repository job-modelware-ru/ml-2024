"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL tno urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from rest_framework import routers
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from MainApp.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

ChannelRouter = routers.DefaultRouter()
ChannelRouter.register(r'channel', ChannelViewSet)

ChannelGroupRouter = routers.DefaultRouter()
ChannelGroupRouter.register(r'channel-group', ChannelGroupViewSet)

VideoRouter = routers.DefaultRouter()
VideoRouter.register(r'video', VideoViewSet)

CommentRouter = routers.DefaultRouter()
CommentRouter.register(r'comment', CommentViewSet)

EmotionRouter = routers.DefaultRouter()
EmotionRouter.register(r'emotion', EmotionViewSet)

VideoGroupRouter = routers.DefaultRouter()
VideoGroupRouter.register(r'video-group', VideoGroupViewSet)

RequestRouter = routers.DefaultRouter()
RequestRouter.register(r'request', RequestViewSet)

CalculationResultRouter = routers.DefaultRouter()
CalculationResultRouter.register(r'calculation-result', CalculationResultViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/login/', LoginView.as_view()),
    path('api/v1/refresh/', RefreshView.as_view()),
    path('api/v1/', include(ChannelRouter.urls)),
    path('api/v1/', include(CommentRouter.urls)),
    path('api/v1/', include(EmotionRouter.urls)),
    path('api/v1/', include(ChannelGroupRouter.urls)),
    path('api/v1/', include(VideoRouter.urls)),
    path('api/v1/', include(VideoGroupRouter.urls)),
    path('api/v1/', include(RequestRouter.urls)),
    path('api/v1/', include(CalculationResultRouter.urls)),
    path('api/v1/signup/', SignUp.as_view()),
    path('api/v1/profile/', ProfileView.as_view()),
    path('api/v1/logout/', LogoutView.as_view()),
    path('api/v1/reset-password/', ResetPasswordView.as_view()),
    path('api/v1/email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('api/v1/add-video-to-group/', AddVideoToGroupView.as_view()),
    path('api/v1/add-channel-to-group/', AddChannelToGroupView.as_view()),
    path('api/v1/send-verification-link/', SendVerificationLink.as_view()),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
