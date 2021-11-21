import django_tables2 as tables
from obywatele.models import Uzytkownik

# https://django-tables2.readthedocs.io/en/latest/pages/filtering.html

class UzytkownikTable(tables.Table):
    class Meta:
        model = Uzytkownik
        fields = ('uid', 'city', 'responsibilities', 'hobby', 'to_give_away', 'to_borrow', 'for_sale', 'i_need', 'skills', 'knowledge', 'want_to_learn', 'business', 'job', 'other')
        # template_name = "django_tables2/bootstrap.html"
        # template_name = "django_tables2/bootstrap-responsive.html"
        # export_formats = ['csv', 'xlsx']
        # exclude = ('id', 'polecajacy', 'data_przyjecia', 'foto', 'phone', 'reputation')
