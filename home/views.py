from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from glosowania.views import ZliczajWszystko
from glosowania.models import Decyzja


def home(request):
    trwajace = Decyzja.objects.filter(status=4)
    zblizajace_sie = Decyzja.objects.filter(status=3).order_by('data_referendum')

    data_referendum = ZliczajWszystko.kolejka
    # TODO: Aktualnie trwające referenda
    # Decyzja.objects.filter(status=0)
    # Decyzja.objects.all().order_by('-data_powstania')
    # print(decyzje)
    # print(kolejka)
    return render(request, 'home/home.html', {'trwajace': trwajace, 'zblizajace_sie': zblizajace_sie, 'data_referendum': data_referendum})


# class Home:
#     def home(request):
#         kolejka = ZliczajWszystko.kolejka()
#         decyzje = Decyzja.objects.all()
#         print(decyzje)
#         print(kolejka)
#         return render(request, 'home/home.html', {'decyzje': decyzje, 'kolejka': kolejka})


def haslo(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Twoje hasło zostało zmienione.')
            return redirect('haslo')
        else:
            messages.error(request, 'Coś źle wpisałeś. Zobacz jaki błąd pojawił się powyżej i spróbuj jeszcze raz.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'home/haslo.html', {
        'form': form
    })

'''
#Tak było kiedyś ale nie wiadomo dlaczego. Jak się pojawi ktoś kto wie to będziemy myśleli o przywróceniu tego. 20160501

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import datetime

def index(request):
    # return render_to_response('home/home.html')
    return render_to_response('home/home.html', context_instance=RequestContext(request))
'''
