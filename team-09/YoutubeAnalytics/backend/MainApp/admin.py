from django.contrib import admin

from MainApp.models import *


@admin.register(Channel, ChannelGroup, Video, Comment, VideoGroup, RequestType, Request, CalculationResult, User,
                ApiKeys)
class PersonAdmin(admin.ModelAdmin):
    pass
