from datetime import datetime, timedelta
from glosowania.models import Decyzja, ZebranePodpisy, KtoJuzGlosowal, VoteCode
from glosowania.forms import DecyzjaForm
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.shortcuts import render
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
import threading
import random
import re


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
            form.author = request.user
            form.data_powstania = datetime.today()
            form.ile_osob_podpisalo += 1
            form.save()
            signed = ZebranePodpisy.objects.create(projekt=form, podpis_uzytkownika = request.user)
            
            # l.warning(f"{form.author} _('added new law proposal:' form.tresc)")
            message = _("New proposal has been saved.")
            messages.success(request, (message))

            SendEmail(
                _('New law proposal'),
                f'{request.user.username.capitalize()} ' + str(_('added new law proposal\nYou can read it here:')) + f' http://{HOST}/glosowania/details/{str(form.id)}'
                )
            return redirect('glosowania:status', 1)
        else:
            return render(request, 'glosowania/dodaj.html', {'form': form})
    else:
        form = DecyzjaForm()
    return render(request, 'glosowania/dodaj.html', {'form': form})


@login_required
def edit(request, pk):
    decision = Decyzja.objects.get(pk=pk)

    if request.method == 'POST':
        form = DecyzjaForm(request.POST)
        if form.is_valid():
            decision.author = request.user
            decision.title = form.cleaned_data['title']
            decision.tresc = form.cleaned_data['tresc']
            decision.kara = form.cleaned_data['kara']
            decision.uzasadnienie = form.cleaned_data['uzasadnienie']
            decision.args_for = form.cleaned_data['args_for']
            decision.args_against = form.cleaned_data['args_against']
            decision.znosi = form.cleaned_data['znosi']
            decision.save()
            message = _("Saved.")
            messages.success(request, (message))

            SendEmail(
                str(_('Proposal')) + f' {str(decision.id)}' + str(_(' has been modified')),
                f'{request.user.username.capitalize()} ' + str(_('modified proposal\nYou can read new version here:')) + f' http://{HOST}/glosowania/details/{str(decision.id)}'
                )
            return redirect('glosowania:status', 1)
    else:  # request.method != 'POST':
        form = DecyzjaForm(initial={
            'author': decision.author,
            'title': decision.title,
            'tresc': decision.tresc,
            'kara': decision.kara,
            'uzasadnienie': decision.uzasadnienie,
            'args_for': decision.args_for,
            'args_against': decision.args_against,
            'znosi': decision.znosi,
        }
        )
    return render(request, 'glosowania/edit.html', {'form': form})


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


def generate_code():
    return''.join([random.SystemRandom().choice('abcdefghjkmnoprstuvwxyz23456789') for i in range(6)])


# Pokaż szczegóły przepisu
@login_required
def details(request, pk):

    zliczaj_wszystko()  # when link from email is used - this is only place Referendum status can be recounted.

    szczegoly = get_object_or_404(Decyzja, pk=pk)

    if request.GET.get('sign'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_podpisujaca = request.user
        podpis = ZebranePodpisy(projekt=nowy_projekt, podpis_uzytkownika=osoba_podpisujaca)
        nowy_projekt.ile_osob_podpisalo += 1
        podpis.save()
        nowy_projekt.save()
        message = _('You signed this motion for a referendum.')
        messages.success(request, (message))
        return redirect('glosowania:details', pk)

    if request.GET.get('withdraw'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_podpisujaca = request.user
        podpis = ZebranePodpisy.objects.get(projekt=nowy_projekt, podpis_uzytkownika=osoba_podpisujaca)
        podpis.delete()
        nowy_projekt.ile_osob_podpisalo -= 1
        nowy_projekt.save()
        message = _('Not signed.')
        messages.success(request, (message))
        return redirect('glosowania:details', pk)

    if request.GET.get('tak'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(
                              projekt=nowy_projekt,
                              ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca
                             )
        nowy_projekt.za += 1
        glos.save()
        nowy_projekt.save()
        
        # TODO: Kod oddanego głosu
        # - wygeneruj kod
        # - tak
        # - projekt
        # - zapisz
        # - wyswietl
        code = generate_code()
        report = VoteCode.objects.create(project=nowy_projekt, code=code, vote=True)

        message1 = str(_('Your vote has been saved. You voted Yes.'))
        messages.success(request, (message1))

        message2 = str(_('Your verification code is:') + f' {code} ')
        messages.error(request, (message2))

        message3 = str(_('Write down your code or create screenshot to verify it when the referendum is over. This code will be presented just once and will be not related to you.'))
        messages.info(request, (message3))

        return redirect('glosowania:details', pk)

    if request.GET.get('nie'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(projekt=nowy_projekt, ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca)
        nowy_projekt.przeciw += 1
        glos.save()
        nowy_projekt.save()

        # TODO: Kod oddanego głosu
        # - wygeneruj kod
        # - nie
        # - projekt
        # - zapisz
        # - wyswietl
        code = generate_code()
        report = VoteCode.objects.create(project=nowy_projekt, code=code, vote=False)

        message1 = str(_('Your vote has been saved. You voted No.'))
        messages.success(request, (message1))

        message2 = str(_('Your verification code is:') + f' {code} ')
        messages.error(request, (message2))

        message3 = str(_('Write down your code or create screenshot to verify it when the referendum is over. This code will be presented just once and will be not related to you.'))
        messages.info(request, (message3))

        return redirect('glosowania:details', pk)

    # check if already signed
    signed = ZebranePodpisy.objects.filter(projekt=pk, podpis_uzytkownika=request.user).exists()

    # check if already voted
    voted = KtoJuzGlosowal.objects.filter(projekt=pk, ktory_uzytkownik_juz_zaglosowal=request.user).exists()

    # Report
    report = VoteCode.objects.filter(project_id=pk)

    # State dictionary
    state = {1: _('Proposal'), 2: _('Rejected'), 3: _('Queued'), 4: _('Referendum'), 5: _('Rejected'), 6: _('Vacatio Legis'), 7: _('Governing Law'), }

    # Corrected data_referendum_stop
    corrected_data_referendum_stop = None
    if szczegoly.data_referendum_stop:
        corrected_data_referendum_stop = szczegoly.data_referendum_stop - timedelta(days=1)

    # Previous and Next
    obj = get_object_or_404(Decyzja, pk=pk)
    prev = Decyzja.objects.filter(pk__lt=obj.pk, status = szczegoly.status).order_by('-pk').first()
    next = Decyzja.objects.filter(pk__gt=obj.pk, status = szczegoly.status).order_by('pk').first()
    
    return render(request, 'glosowania/szczegoly.html', {'id': szczegoly,
                                                         'signed': signed,
                                                         'voted': voted,
                                                         'report': report,
                                                         'current_user': request.user,
                                                         'state': state[szczegoly.status],
                                                         'corrected_data_referendum_stop': corrected_data_referendum_stop,
                                                         'prev': prev,
                                                         'next': next,
                                                         })


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

                # TODO: Referendum rozpocznie się za 1 tydzień w poniedziałek
                # 0 = monday, 1 = tuesday, ..., 6 = sunday
                i.data_referendum_start = i.data_zebrania_podpisow + timedelta(days=s.KOLEJKA) + timedelta(days=-dzisiaj.weekday()+0, weeks=1)
                i.data_referendum_stop = i.data_referendum_start + timedelta(days=s.CZAS_TRWANIA_REFERENDUM)
                i.save()
                SendEmail(
                    str(_("Proposal no.")) + " " + str(i.id) + " " + str(_("is approved for referendum")),
                    str(_("Proposal no.")) + " " + str(i.id) + " " +
                    str(_("gathered required amount of signatures and will be voted from")) + " " +
                    str(i.data_referendum_start) + " " + str(_('to')) + " " + str(i.data_referendum_stop) +
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
                    str(_("Proposal no.")) + " " + str(i.id) + " " + str(_("didn't gathered required amount of signatures")),
                    str(_("Proposal no.")) + " " + str(i.id) + " " +
                    str(_("didn't gathered required amount of signatures")) + " " + str(_("and was removed from queue.")) + " " +
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
                    str(_("Referendum on proposal no.")) + " " + str(i.id) + " " + str(_("is starting now")),
                    str(_("It is time to vote on proposal no.")) + " " + str(i.id) + '\n' +
                    str(_("Referendum ends at")) + " " +
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
                    str(_("Proposal no.")) + " " + str(i.id) + str(_("was approved")),
                    str(_("Proposal no.")) + " " + str(i.id) + " " +
                    str(_("was approved in referendum and is now in Vacatio Legis period")) + '.\n' +
                    str(_("The law will take effect on")) + " " + 
                    str(i.data_obowiazuje_od) + '\n' + str(_("Click here to read proposal: http://")) + 
                    f"{HOST}/glosowania/details/{str(i.id)}"
                    )
                    continue
                else:
                    i.status = odrzucone
                    i.save()
                    # log('Propozycja ' + str(i.id) + ' zmieniła status na "odrzucone"')
                    SendEmail(
                    str(_("Proposal no.")) + " " + str(i.id) + str(_("was rejected")),
                    str(_("Proposal no.")) + " " + str(i.id) + " " +
                    str(_("was rejected in referendum.")) + '\n' + 
                    str(_("Feel free to improve it and send it again.")) +
                    '\n' + str(_("Click here to read proposal: http://")) + 
                    f"{HOST}/glosowania/details/{str(i.id)}"
                    )
                    continue

            # FROM VACATIO_LEGIS TO LAW
            if i.status == zatwierdzone and i.data_obowiazuje_od <= dzisiaj:
                i.status = obowiazuje
                
                # Reject bills
                if i.znosi:
                    separated = re.split('\W+', i.znosi)
                    for z in separated:
                        abolish = Decyzja.objects.get(pk=str(z))
                        abolish.status = 5
                        abolish.save()
                
                i.save()

                # log('Propozycja ' + str(i.id) + ' zmieniła status na "obowiązuje".')
                SendEmail(
                str(_("Proposal no.")) + " " + str(i.id) + " " + str(_("is in efect from today")),
                str(_("Proposal no.")) + " " + str(i.id) + " " + str(_("became abiding law today")) + '.\n' + 
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
    
    t = threading.Thread(
                         target=email_message.send,
                         args=("fail_silently=False",)
                        )
    t.setDaemon(True)
    t.start()
