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
from django.conf import settings as s
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
import logging as l
from django.utils import translation

l.basicConfig(filename='wiki.log', datefmt='%d-%b-%y %H:%M:%S', format='%(asctime)s %(levelname)s %(funcName)s() %(message)s', level=l.INFO)

HOST = s.ALLOWED_HOSTS[0]
# ROOT = s.BASE_DIR

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
            
            # l.warning(f"{form.autor} _('added new law proposal:' form.tresc)")
            message = _("New proposal has been saved.")
            messages.success(request, (message))

            SendEmail(
                _('New law proposal'),
                f'{request.user.username.capitalize()} ' + str(_('added new law proposal\nYou can read it here:')) + f' http://{HOST}/glosowania/details/{str(form.id)}'
                )
            return redirect('glosowania:status', 1)
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
def status(request, pk):
    filtered_glosowania = Decyzja.objects.filter(status=pk)
    lang = get_language()

    zliczaj_wszystko()
    return render(request, 'glosowania/status.html', {
        'filtered_glosowania': filtered_glosowania,
        'lang': lang[0:2],  # just en instead of en-us
        'signatures': s.WYMAGANYCH_PODPISOW,
        'signatures_span': timedelta(days=s.CZAS_NA_ZEBRANIE_PODPISOW).days,
        'queue_span': timedelta(days=s.KOLEJKA).days,
        'referendum_span': timedelta(days=s.CZAS_TRWANIA_REFERENDUM).days,
        'vacatio_legis_span': timedelta(days=s.VACATIO_LEGIS).days,
    })


# Pokaż szczegóły przepisu
@login_required
def details(request, pk):
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
        return redirect('glosowania:details', pk)

    if request.GET.get('tak'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(projekt=nowy_projekt, ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca)
        nowy_projekt.za += 1
        glos.save()
        nowy_projekt.save()
        message = _('Your vote has been saved. You voted Yes.')
        messages.success(request, (message))
        return redirect('glosowania:details', pk)

    if request.GET.get('nie'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(projekt=nowy_projekt, ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca)
        nowy_projekt.przeciw += 1
        glos.save()
        nowy_projekt.save()
        message = _('Your vote has been saved. You voted No.')
        messages.success(request, (message))
        return redirect('glosowania:details', pk)

    # check if already signed
    signed = ZebranePodpisy.objects.filter(projekt=pk, podpis_uzytkownika=request.user).exists()

    # check if already voted
    voted = KtoJuzGlosowal.objects.filter(projekt=pk, ktory_uzytkownik_juz_zaglosowal=request.user).exists()

    return render(request, 'glosowania/szczegoly.html', {'id': szczegoly, 'signed': signed, 'voted': voted})


def zliczaj_wszystko():
    '''Jeśli propozycja zostanie zatwierdzona w niedzielę
    to głosowanie odbędzie się za 2 tygodnie'''

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
            if i.status == propozycja and i.ile_osob_podpisalo >= s.WYMAGANYCH_PODPISOW:
                i.status = w_kolejce
                i.data_zebrania_podpisow = dzisiaj

                # TODO: Referendum odbędzie się za 1 tydzień w niedzielę
                # 0 = monday, 1 = tuesday, ..., 6 = sunday
                i.data_referendum_start = i.data_zebrania_podpisow + timedelta(days=s.KOLEJKA) + timedelta(days=-dzisiaj.weekday()+0, weeks=1)
                i.data_referendum_stop = i.data_referendum_start + timedelta(days=s.CZAS_TRWANIA_REFERENDUM)
                i.save()
                SendEmail(
                    str(_("Proposal no. ")) + str(i.id) + str(_(" is approved for referendum")),
                    str(_("Proposal no. ")) + str(i.id) +
                    str(_(" gathered required amount of signatures and will be voted from ")) +
                    str(i.data_referendum_start) + str(_(' to ')) + str(i.data_referendum_stop) +
                    '\n' + str(_("Click here to read proposal: http://")) +
                    f"{HOST}/glosowania/details/{str(i.id)}"
                )
                continue

            # FROM PROPOSITION TO NO_INTREST
            if i.status == propozycja and i.data_powstania + timedelta(days=s.CZAS_NA_ZEBRANIE_PODPISOW) <= dzisiaj:
                i.status = brak_poparcia
                i.save()
                # log('Propozycja ' + str(i.id) + ' zmieniła status na "brak poparcia".')
                SendEmail(
                    # _(f"Proposal {str(i.id)} didn't gathered required amount of signatures"),  # translation doesn't work this way
                    str(_("Proposal no. ")) + str(i.id) + str(_(" didn't gathered required amount of signatures")),
                    str(_("Proposal no. ")) + str(i.id) +
                    str(_(" didn't gathered required amount of signatures")) + str(_(" and was removed from queue. ")) +
                    str(_("Feel free to improve it and send it again.")) +
                    '\n' + str(_("Click here to read proposal: http://")) +
                    f"{HOST}/glosowania/details/{str(i.id)}"
                )
                continue

            # FROM QUEUE TO REFERENDUM
            if i.status == w_kolejce and i.data_referendum_start <= dzisiaj:
                i.status = referendum
                i.save()
                # log('Propozycja ' + str(i.id) + ' zmieniła status na "referendum".')
                SendEmail(
                    str(_("Referendum on proposal no. ")) + str(i.id) + str(_(" is starting now")),
                    str(_("It is time to vote on proposal no. ")) + str(i.id) + '\n' +
                    str(_("Referendum ends at ")) + 
                    str(i.data_referendum_stop) + '\n' +
                    str(_("Click here to vote: http://")) + 
                    f"{HOST}/glosowania/details/{str(i.id)}"
                )
                continue

            # FROM REFERENDUM TO VACATIO_LEGIS OR NOT_APPROVED
            if i.status == referendum and i.data_referendum_stop <= dzisiaj:
                if i.za > i.przeciw:
                    i.status = zatwierdzone
                    i.data_zatwierdzenia = i.data_referendum_stop
                    i.data_obowiazuje_od = i.data_referendum_stop + timedelta(days=s.VACATIO_LEGIS)
                    i.save()
                    # log('Propozycja ' + str(i.id) + ' zmieniła status na "zatwierdzone".')
                    SendEmail(
                    str(_("Proposal no. ")) + str(i.id) + str(_("was approved")),
                    str(_("Proposal no. ")) + str(i.id) + 
                    str(_("was approved in referendum and is now in Vacatio Legis period")) + '.\n' +
                    str(_("The law will take effect on")) + 
                    i.data_obowiazuje_od + '\n' + str(_("Click here to read proposal: http://")) + 
                    f"{HOST}/glosowania/details/{str(i.id)}"
                    )
                    continue
                else:
                    i.status = odrzucone
                    i.save()
                    # log('Propozycja ' + str(i.id) + ' zmieniła status na "odrzucone"')
                    SendEmail(
                    str(_("Proposal no. ")) + str(i.id) + str(_("was rejected")),
                    str(_("Proposal no. ")) + str(i.id) +
                    str(_(" was rejected in referendum.")) + '\n' + 
                    str(_("Feel free to improve it and send it again.")) +
                    '\n' + str(_("Click here to read proposal: http://")) + 
                    f"{HOST}/glosowania/details/{str(i.id)}"
                    )
                    continue

            # FROM VACATIO_LEGIS TO LAW
            if i.status == zatwierdzone and i.data_obowiazuje_od <= dzisiaj:
                i.status = obowiazuje
                i.save()
                # log('Propozycja ' + str(i.id) + ' zmieniła status na "obowiązuje".')
                SendEmail(
                str(_("Proposal no. ")) + str(i.id) + str(_(" is in efect from today")),
                str(_("Proposal no. ")) + str(i.id) + str(_(" became abiding law today")) + '.\n' + 
                str(_("Click here to read it: http://")) + 
                f"{HOST}/glosowania/details/{str(i.id)}"
                )
                continue


def SendEmail(subject, message):
    # bcc: all active users
    # subject: Custom
    # message: Custom
    translation.activate(s.LANGUAGE_CODE)

    email_message = EmailMessage(
        from_email=str(s.DEFAULT_FROM_EMAIL),
        bcc = list(User.objects.filter(is_active=True).values_list('email', flat=True)),
        subject=f'{HOST} - {subject}',
        body=message,
        )
    # l.warning(f'subject: {subject} \n message: {message}')
    email_message.send(fail_silently=False)
