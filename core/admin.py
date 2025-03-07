from django.contrib import admin
from .models import Collection, Entry, Friendship

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'collection', 'user', 'status', 'visibility', 'created_at')
    list_filter = ('status', 'visibility', 'collection', 'user')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'friend__username')
