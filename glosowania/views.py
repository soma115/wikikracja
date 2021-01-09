from datetime import datetime, timedelta
from glosowania.models import Decyzja, ZebranePodpisy, KtoJuzGlosowal
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.shortcuts import render
from glosowania.forms import DecyzjaForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
import logging as l


l.basicConfig(filename='wiki.log', datefmt='%d-%b-%y %H:%M:%S', format='%(asctime)s %(levelname)s %(funcName)s() %(message)s', level=l.INFO)

HOST = settings.ALLOWED_HOSTS[0]
# ROOT = settings.BASE_DIR

# Dodaj nową propozycję przepisu:
@login_required
def dodaj(request):
    # nowy = DecyzjaForm(request.POST or None)
    if request.method == 'POST':
        form = DecyzjaForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.autor = request.user
            form.data_powstania = datetime.today()
            form.ile_osob_podpisalo += 1
            form.save()
            signed = ZebranePodpisy.objects.create(projekt=form, podpis_uzytkownika = request.user)
            
            # l.info(form.autor)
            message = _("New proposition has been saved.")
            messages.success(request, (message))

            SendEmail(
                _('New law proposition'),
                _(f'{request.user.username.capitalize()} added new law proposition\nYou can read it here: http://{HOST}/glosowania/{str(form.id)}')
                )
            return HttpResponseRedirect('/glosowania/?1=1.+Nowa+propozycja#')
            # return redirect('glosowania:glosowania')
    else:
        form = DecyzjaForm()
    return render(request, 'glosowania/dodaj.html', {'form': form})


@login_required
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    username = None

    if request.user.is_authenticated():
        username = request.user.username

    with open('access.log', 'a') as log:
        log.writelines(f"{datetime.now()} {ip} {username}\n")


# Wyświetl głosowania:
@login_required
def glosowania(request):
    # get_client_ip(request) # logowanie
    lang = get_language()

    # print(request.body)
    # print(request.scheme)
    # print(request.path)
    # print(request.content_params)
    # print(request.GET)
    # print(request.POST)
    # print(request.resolver_match)
    # print(request.current_app)
    # print(request.headers)

    # if request.method == 'GET':
    #     for i in request.GET.items():
    #         print(i)
    #         x = i[0]
    # decyzje = Decyzja.objects.filter(status=x)
    # print(x)

    # TODO: Guziki będą się zapalały więc nie trzeba pola 'status'
    # TODO: Wtedy będzie można zrobić jeden return i dzięki temu będzie można łatwo zrobić 'Voting parameters'

    

    if request.GET.get("1"):
        decyzje = Decyzja.objects.filter(status=1)
        return render(request, 'glosowania/start.html',
                            {
                                'decyzje': decyzje,
                                'status': _("New propositions"),
                                'lang': lang,
                            })

    if request.GET.get("2"):
        decyzje = Decyzja.objects.filter(status=2)
        return render(request, 'glosowania/start.html',
                        {
                          'decyzje': decyzje,
                          'status': _("No endorsement"),
                          'lang': lang,
                        })

    if request.GET.get("3"):
        decyzje = Decyzja.objects.filter(status=3)
        return render(request, 'glosowania/start.html',
                        {
                            'decyzje': decyzje,
                            'status': _("Queued for referedum"),
                            'lang': lang,
                        })

    if request.GET.get("4"):
        decyzje = Decyzja.objects.filter(status=4)
        return render(request, 'glosowania/start.html',
                        {
                            'decyzje': decyzje,
                            'status': _("Referendum"),
                            'lang': lang,
                        })

    if request.GET.get("5"):
        decyzje = Decyzja.objects.filter(status=5)
        return render(request, 'glosowania/start.html',
                        {
                            'decyzje': decyzje,
                            'status': _("Rejected in referendum"),
                            'lang': lang,
                        })

    if request.GET.get("6"):
        decyzje = Decyzja.objects.filter(status=6)
        return render(request, 'glosowania/start.html',
                        {
                          'decyzje': decyzje,
                          'status': _("Accepted / Vacatio Legis"),
                          'lang': lang,
                        })

    if request.GET.get("7"):
        decyzje = Decyzja.objects.filter(status=7)
        return render(request, 'glosowania/start.html',
                        {
                            'decyzje': decyzje,
                            'status': _("Applicable regulations"),
                            'lang': lang,
                        })

    zliczaj_wszystko()

    decyzje = Decyzja.objects.filter(status=7)
    return render(request, 'glosowania/start.html',
                        {
                            'decyzje': decyzje,
                            'status': _("Applicable regulations"),
                            'lang': lang,
                        })


# Pokaż szczegóły przepisu
@login_required
def glosowanie_szczegoly(request, pk):
    szczegoly = get_object_or_404(Decyzja, pk=pk)

    if request.GET.get('podpisz'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_podpisujaca = request.user
        podpis = ZebranePodpisy(projekt=nowy_projekt, podpis_uzytkownika=osoba_podpisujaca)
        nowy_projekt.ile_osob_podpisalo += 1
        podpis.save()
        nowy_projekt.save()
        message = _('Your signature has been saved.')
        messages.success(request, (message))
        return redirect('glosowania:glosowanie_szczegoly', pk)

    if request.GET.get('tak'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(projekt=nowy_projekt, ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca)
        nowy_projekt.za += 1
        glos.save()
        nowy_projekt.save()
        message = _('Your vote has been saved. You voted Yes.')
        messages.success(request, (message))
        return redirect('glosowania:glosowanie_szczegoly', pk)

    if request.GET.get('nie'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(projekt=nowy_projekt, ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca)
        nowy_projekt.przeciw += 1
        glos.save()
        nowy_projekt.save()
        message = _('Your vote has been saved. You voted No.')
        messages.success(request, (message))
        return redirect('glosowania:glosowanie_szczegoly', pk)

    # check if already signed
    signed = ZebranePodpisy.objects.filter(projekt=pk, podpis_uzytkownika=request.user).exists()

    # check if already voted
    voted = KtoJuzGlosowal.objects.filter(projekt=pk, ktory_uzytkownik_juz_zaglosowal=request.user).exists()

    return render(request, 'glosowania/szczegoly.html', {'id': szczegoly, 'signed': signed, 'voted': voted})


class ZliczajWszystko():
    # TODO: ZliczajWszystko
    # czas pomiędzy zebraniem podpisów a referendum
    # wymagany aby móc omówić skutki:
    kolejka = timedelta(days=7)

    def get(self, request):
        pass
        return HttpResponse('result')


def zliczaj_wszystko():
    '''Jeśli propozycja zostanie zatwierdzona w niedzielę
    to głosowanie odbędzie się za 2 tygodnie'''
    # print('Zliczam głosy i terminy...')
    wymaganych_podpisow = 2  # Aby zatwierdzić wniosek o referendum
    czas_na_zebranie_podpisow = timedelta(days=365)  # 365
    # czas pomiędzy zebraniem podpisów a referendum wymagany aby móc omówić skutki:
    kolejka = timedelta(days=7)
    czas_trwania_referendum = timedelta(days=7)  #
    vacatio_legis = timedelta(days=7)  #

    propozycja = 1
    brak_poparcia = 2
    w_kolejce = 3
    referendum = 4
    odrzucone = 5
    zatwierdzone = 6  # Vacatio Legis
    obowiazuje = 7

    dzisiaj = datetime.today().date()

    decyzje = Decyzja.objects.all()
    for i in decyzje:
        if i.status != brak_poparcia and i.status != odrzucone and i.status != obowiazuje:
            # Jeśli nie jest w jakiś sposób zatwierdzone/odrzucone to procesujemy:

            # FROM PROPOSITION TO QUEUE
            if i.status == propozycja and i.ile_osob_podpisalo >= wymaganych_podpisow:
                i.status = w_kolejce
                i.data_zebrania_podpisow = dzisiaj

                # TODO: Referendum odbędzie się 1 tydzień w niedzielę
                # 0 = monday, 1 = tuesday, ..., 6 = sunday
                i.data_referendum_start = i.data_zebrania_podpisow + kolejka + timedelta(days=-dzisiaj.weekday()+0, weeks=1)
                i.data_referendum_stop = i.data_referendum_start + czas_trwania_referendum
                i.save()
                SendEmail(
                    _(f'Proposition {str(i.id)} approved for referendum'),
                    _(f'Proposition {str(i.id)} gathered required amount of signatures and will be voted from {i.data_referendum_start} to {i.data_referendum_stop}.\nClick here to read proposition: http://{HOST}/glosowania/{str(i.id)}')
                    )
                continue

            # FROM PROPOSITION TO NO_INTREST
            if i.status == propozycja and i.data_powstania + czas_na_zebranie_podpisow <= dzisiaj:
                i.status = brak_poparcia
                i.save()
                # log('Propozycja ' + str(i.id) + ' zmieniła status na "brak poparcia".')
                SendEmail(
                _(f"Proposition {str(i.id)} didn't gathered required amount of signatures"),
                _(f"Proposition {str(i.id)} didn't gathered required amount of signatures and was removed from queue. Feel free to improve it and send it again.\nClick here to read proposition: http://{HOST}/glosowania/{str(i.id)}")
                )
                continue

            # FROM QUEUE TO REFERENDUM
            if i.status == w_kolejce and i.data_referendum_start <= dzisiaj:
                i.status = referendum
                i.save()
                # log('Propozycja ' + str(i.id) + ' zmieniła status na "referendum".')
                SendEmail(
                _(f'Referendum on proposition {str(i.id)} starting now'),
                _(f'It is time to vote on proposition {str(i.id)}.\nReferendum ends at {i.data_referendum_stop}.\nClick here to vote: http://{HOST}/glosowania/{str(i.id)}')
                )
                continue

            # FROM REFERENDUM TO VACATIO_LEGIS OR NOT_APPROVED
            if i.status == referendum and i.data_referendum_stop <= dzisiaj:
                if i.za > i.przeciw:
                    i.status = zatwierdzone
                    i.data_zatwierdzenia = i.data_referendum_stop
                    i.data_obowiazuje_od = i.data_referendum_stop + vacatio_legis
                    i.save()
                    # log('Propozycja ' + str(i.id) + ' zmieniła status na "zatwierdzone".')
                    SendEmail(
                    _(f'Proposition {str(i.id)} approved'),
                    _(f'Proposition {str(i.id)} was approved in referendum and is now in Vacatio Legis period.\nThe law will take effect on {i.data_obowiazuje_od}.\nClick here to read proposition: http://{HOST}/glosowania/{str(i.id)}')
                    )
                    continue
                else:
                    i.status = odrzucone
                    i.save()
                    # log('Propozycja ' + str(i.id) + ' zmieniła status na "odrzucone"')
                    SendEmail(
                    _(f'Proposition {str(i.id)} rejected'),
                    _(f'Proposition {str(i.id)} was rejected in referendum.\nFeel free to improve it and send it again.\nClick here to read proposition: http://{HOST}/glosowania/{str(i.id)}')
                    )
                    continue

            # FROM VACATIO_LEGIS TO LAW
            if i.status == zatwierdzone and i.data_obowiazuje_od <= dzisiaj:
                i.status = obowiazuje
                i.save()
                # log('Propozycja ' + str(i.id) + ' zmieniła status na "obowiązuje".')
                SendEmail(
                _(f'Proposition {str(i.id)} is in efect from today'),
                _(f'Proposition {str(i.id)} became abiding law today.\nClick here to read proposition: http://{HOST}/glosowania/{str(i.id)}')
                )
                continue


def SendEmail(subject, message):
    # bcc: all active users
    # subject: Custom
    # message: Custom

    email_message = EmailMessage(
        from_email=str(settings.DEFAULT_FROM_EMAIL),
        bcc = list(User.objects.filter(is_active=True).values_list('email', flat=True)),
        subject=f'{HOST} - {subject}',
        body=message,
        )
    l.info(f'subject: {subject} \n message: {message}')
    email_message.send(fail_silently=False)
