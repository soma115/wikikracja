from django.contrib import admin
from glosowania.models import Decyzja


class NoweGlosowanie(admin.ModelAdmin):
    pass
    # fields = ('tresc',)
    # inlines = [CommentInline]

    # def save_model(self, request, obj, form, change):
    #     obj.user = request.user
    #     obj.save()

    # def save_formset(self, request, form, formset, change):
    #     if formset.model == Comment:
    #         instances = formset.save(commit=False)
    #         for instance in instances:
    #             instance.user = request.user
    #             instance.save()
    #     else:
    #         formset.save()


admin.site.register(Decyzja)
