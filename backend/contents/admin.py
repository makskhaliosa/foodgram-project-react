from django.contrib import admin

from .core.utils import get_measure_form
from .models import (
    Tag, Ingredient, Recipe, TagRecipe, IngredientRecipe, Favorites,
    ShoppingCart, Subscriptions)


class TagInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 2


class TagAdmin(admin.ModelAdmin):
    inlines = (TagInline,)
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    search_fields = (
        'author__username', 'author__first_name',
        'name', 'tags__name', 'tags__slug')
    readonly_fields = ('favorites_number',)
    list_filter = ('tags',)
    inlines = (IngredientInline, TagInline)

    @admin.display(description='Добавлено в избранное')
    def favorites_number(self, obj):
        """Число добавлений в избранное."""
        obj_count = str(obj.favorites.count())
        measure = get_measure_form(obj_count)
        return f'{obj_count} {measure}'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(TagRecipe)
admin.site.register(IngredientRecipe)
admin.site.register(Favorites)
admin.site.register(Subscriptions)
admin.site.register(ShoppingCart)
