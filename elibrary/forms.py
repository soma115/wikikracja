from django import forms
from elibrary.models import Book
from django.utils.translation import gettext as _

class UpdateBookForm(forms.ModelForm):
    title = forms.CharField(max_length=200, label=_('Title'))
    author = forms.CharField(max_length=200, label=_('Author'), required=False)
    cover = forms.ImageField(required=False, label=_('Cover'))
    # tag = forms.CharField(required=False)
    file_epub = forms.FileField(required=False, label=_('File epub'))
    file_mobi = forms.FileField(required=False, label=_('File mobi'))
    file_pdf = forms.FileField(required=False, label=_('File pdf'))
    # uploader is added autmatically in Views

    class Meta:
        model = Book
        # fields = ('title', 'author', 'cover', 'tag', 'file_epub', 'file_mobi', 'file_pdf',)
        fields = ('title', 'author', 'cover', 'file_epub', 'file_mobi', 'file_pdf',)
