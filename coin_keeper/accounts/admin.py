from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from .models import CustomUser, Stato, Moneta, Luogo, Esemplare


# Branding dell'admin
admin.site.site_header = settings.ADMIN_SITE_HEADER if hasattr(settings, "ADMIN_SITE_HEADER") else "Coin Keeper Admin"
admin.site.site_title = settings.ADMIN_SITE_TITLE if hasattr(settings, "ADMIN_SITE_TITLE") else "Coin Keeper Portal"
admin.site.index_title = settings.ADMIN_INDEX_TITLE if hasattr(settings, "ADMIN_INDEX_TITLE") else "Pannello di controllo"


# Admin per CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "is_verified", "is_staff", "is_active")
    list_filter = ("is_verified", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("is_verified",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("is_verified",)}),
    )


# Admin per Stato
@admin.register(Stato)
class StatoAdmin(admin.ModelAdmin):
    list_display = ("nome", "iso2")
    search_fields = ("nome", "iso2")
    ordering = ("nome",)


# Admin per Moneta
@admin.register(Moneta)
class MonetaAdmin(admin.ModelAdmin):
    list_display = ("valore_nominale", "anno_conio", "stato")
    list_filter = ("stato", "anno_conio")
    search_fields = ("valore_nominale",)
    ordering = ("stato", "anno_conio")


# Admin per Luogo
@admin.register(Luogo)
class LuogoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    ordering = ("nome",)


# Admin per Esemplare
@admin.register(Esemplare)
class EsemplareAdmin(admin.ModelAdmin):
    list_display = ("utente", "moneta", "luogo", "note")
    list_filter = ("utente", "moneta__stato", "luogo", "moneta__anno_conio")
    search_fields = ("utente__username", "moneta__valore_nominale", "note")
    ordering = ("utente", "moneta")
    list_editable = ("note",)  # modificabile direttamente dalla lista
