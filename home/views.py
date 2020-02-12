from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from glosowania.views import ZliczajWszystko
from glosowania.models import Decyzja
from django.contrib.auth.decorators import login_required


def home(request):
    trwajace = Decyzja.objects.filter(status=4)
    zblizajace_sie = Decyzja.objects.filter(status=3).order_by('data_referendum_start')

    data_referendum_start = ZliczajWszystko.kolejka
    # TODO: Aktualnie trwające referenda
    # Decyzja.objects.filter(status=0)
    # Decyzja.objects.all().order_by('-data_powstania')
    # print(decyzje)
    # print(kolejka)
    return render(request,
                  'home/home.html',
                  {'trwajace': trwajace,
                   'zblizajace_sie': zblizajace_sie,
                   'data_referendum_start': data_referendum_start}
                  )

# class Home:
#     def home(request):
#         kolejka = ZliczajWszystko.kolejka()
#         decyzje = Decyzja.objects.all()
#         print(decyzje)
#         print(kolejka)
#         return render(request, 'home/home.html', {'decyzje': decyzje,
#                                                   'kolejka': kolejka})


@login_required
def haslo(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Twoje hasło zostało zmienione.')
            return redirect('haslo')
        else:
            messages.error(request, 'Coś źle wpisałeś. Zobacz jaki błąd pojawił \
                                     się powyżej i spróbuj jeszcze raz.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'home/haslo.html', {
        'form': form
    })
