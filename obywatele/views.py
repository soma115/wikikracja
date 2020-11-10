from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.models import User
from obywatele.forms import ObywatelForm
from obywatele.models import Uzytkownik, Rate
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
import random
import string
from django.utils.timezone import now as dzis
from math import log
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg, Sum
import logging as l

l.basicConfig(filename='wiki.log', datefmt='%d-%b-%y %H:%M:%S', format='%(asctime)s %(levelname)s %(funcName)s() %(message)s', level=l.INFO)

# Higher limit seams to be problematic bacuse people rarely acctepting each
# other.
ACCEPTANCE_MULTIPLIER = 1.6


@login_required
def obywatele(request):
    zliczaj_obywateli(request)  # TODO: show puplation on page Obywatele
    uid = User.objects.filter(is_active=True)
    # TODO: dodać datę przyjęcia do szczegółów każdego użytkownika
    return render(request, 'obywatele/start.html', {'uid': uid})


@login_required
def poczekalnia(request):
    uid = User.objects.filter(is_active=False)
    return render(request, 'obywatele/poczekalnia.html', {'uid': uid})


@login_required
def dodaj(request):
    if request.method == 'POST':
        form = ObywatelForm(request.POST)
        if form.is_valid():
            mail = form.cleaned_data['email']
            nick = form.cleaned_data['username']

            if User.objects.filter(email=mail).exists():
                # is_valid doesn't check if email exist
                wynik = 'Email już istnieje'
                return render(request,
                              'obywatele/zapisane.html',
                              {'wynik': wynik, })

            else:
                # If everything is ok
                form.save()
                candidate = User.objects.get(username=nick)
                candidate.is_active = False
                candidate.save()

                candidate_profile = Uzytkownik.objects.get(id=candidate.id)
                candidate_profile.polecajacy = request.user.username
                candidate_profile.save()

                # Since you proposed new person,
                # you probably also want to accept him/her
                citizen = Uzytkownik.objects.get(pk=request.user.id)
                rate = Rate()
                rate.obywatel = citizen
                rate.kandydat = candidate_profile
                rate.rate = 1
                rate.save()

                wynik = 'Nowy użytkownik został zapisany'
                return render(request,
                              'obywatele/zapisane.html',
                              {'wynik': wynik, })
        else:
            wynik = form.errors
            return render(request,
                          'obywatele/zapisane.html',
                          {'wynik': wynik, })

    form = ObywatelForm()
    return render(request, 'obywatele/dodaj.html', {'form': form})


@login_required
def obywatele_szczegoly(request, pk):
    '''BUG:  Reputation is calculated inorrectly.
    -[x] There has to be a table relating user and new person. This table is
    needed because vote for person may be withdrawn at some point. So there
    are 3 states:
      1. Candidate is positive
      2. Candidate is neutral (not clicked, default)
      3. Candidate is negative
    3 states are needed because:
      - this is a fact, those 3 states really exist
      - but most importantly: it should be possible to take reputation
        away - even if somebody did not give reputation to that person
        before.

    -[ ] Reputation should be calculated from Ratetable relating citizen and candidate.

    -[ ] Counter should be zeroed out if person drop below required reputation. Then user is deactivated and counting starts from 0.

    -[ ] New person increase population so also increase reputation equirements. Therefore every time new person is accepted - every other old member should have his reputation increased autmatically. And vice versa - if somebody is banned - everyone else should loose one point of reputation from banned person.'''

    citizen = Uzytkownik.objects.get(pk=request.user.id)

    candidate_profile = get_object_or_404(Uzytkownik, pk=pk)
    candidate = str(User.objects.get(pk=pk))

    population = User.objects.filter(is_active=True).count()
    required_reputation = int(log(population) * ACCEPTANCE_MULTIPLIER)
    citizen_reputation = citizen.reputation

    if candidate_profile == citizen:
        return render(request,
                      'obywatele/szczegoly.html',
                      {'b': candidate_profile,
                       'd': citizen,
                       'tr': citizen_reputation,
                       'wr': required_reputation})

    # print('-----------------', candidate_profile)
    # print('-----------------', citizen)
    rate = Rate.objects.get_or_create(kandydat=candidate_profile, obywatel=citizen)[0]
    # print('-----------------', rate.rate)

    if request.GET.get('tak'):
        rate.rate = 1
        rate.save()
        wynik = 'Twój stosunek do użytkownika ' + candidate + ' jest pozytywny.'
        return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

    if request.GET.get('nie'):
        rate.rate = -1
        rate.save()

        wynik = 'Twój stosunek do użytkownika ' + candidate + ' jest negatywny.'
        return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

    if request.GET.get('reset'):
        rate.rate = 0
        rate.save()

        wynik = 'Twój stosunek do użytkownika ' + candidate + ' jest neutralny.'
        return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

    if rate.rate == -1:
        r1 = _('negative')
    if rate.rate == 0:
        r1 = _('neutral')
    if rate.rate == 1:
        r1 = _('positive')

    return render(
        request,
        'obywatele/szczegoly.html',
        {
            'b': candidate_profile,
            'd': citizen,
            'tr': citizen_reputation,
            'wr': required_reputation,
            'rate': r1
        })


# TODO: zamienić na obiekt z metodą: "podaj obecną populację":
def zliczaj_obywateli(request):
    '''
    -[ ] Count everyones reputation from Rate model and put it in to Uzytkownik
    -[ ] Calculate population and required reputation
    -[ ] Run through all user and check if somebody jumped above or below threshold:
        -[ ] If jumped above - enable user and add 1 reputation to all other users
        -[ ] If jumped bellow - disable user and remove 1 reputation from all other users

    Acceptance simulator: scripts/acceptance_simulator.py
    '''

    population = User.objects.filter(is_active=True).count()
    required_reputation = round(log(population) * ACCEPTANCE_MULTIPLIER)
    # akceptacja = Rate()

    # Count everyones reputation from Rate model and
    # put it in to Uzytkownik
    for i in Uzytkownik.objects.all():
        
        # print(i.uid)
        # tt = Rate.objects.get_or_create(obywatel=i, defaults={'obywatel': i, 'kandydat': i, 'rate': '0'})
        # print(tt)

        if Rate.objects.filter(kandydat=i).exists():
            reputation = Rate.objects.filter(kandydat=i).aggregate(Sum('rate'))
            i.reputation = list(reputation.values())[0]
            # l.info(f'Candidate: {i.uid.id}; Reputation: {list(reputation.values())[0]};')
            i.save()


    # Włącz użytkowników z odpowiednio wysoką reputacją
    for i in Uzytkownik.objects.all():
        if i.reputation > required_reputation and not i.uid.is_active:
            i.uid.is_active = True  # Uzytkownik.uid -> User
            password = password_generator()
            i.uid.set_password(password)
            i.data_przyjecia = dzis()
            i.uid.save()
            l.info(f'Activating user {i.uid}')
            i.save()

            # Nadaj wszystkim pozostałym 1 punkt reputacji
            # for j in Uzytkownik.objects.all():
            #     if i != j:
            #         j.reputation += 1
            #         j.save()
            
            # New person accepts automatically everyone
            for k in Uzytkownik.objects.all():
                if i == k:    # but not yourself
                    continue
                akceptacja = Rate()
                akceptacja.obywatel = i
                akceptacja.kandydat = k
                akceptacja.rate = 1
                try:
                    akceptacja.save()
                except:  # TODO: except something
                    continue

            subject = request.get_host() + ' - Twoje konto zostało włączone'
            uname = str(i.uid.username)
            uhost = str(request.get_host())
            message = f'Witaj {uname}\nTwoje konto na {uhost} zostało włączone.\n\nTwój login to: {uname}\nTwoje hasło to: {password}\n\nZaloguj się tutaj: {uhost}/login/\n\nHasło możesz zmienić tutaj: {uhost}/haslo/'

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      [i.uid.email], fail_silently=False)

    # Blokuj użytkowników ze zbyt niską reputacją
    for i in Uzytkownik.objects.all():
        # l.info(f'Uzytkownik {i.id} reputation: {i.reputation}')
        if i.reputation < required_reputation and i.uid.is_active:
            i.uid.is_active = False  # Uzytkownik.uid -> User
            i.uid.save()
            l.info(f'Blocking user {i.uid}')
            i.save()

            # Odbierz wszystkim pozostałym 1 punkt reputacji
            # for j in Uzytkownik.objects.all():
            #     # print(j.uid)
            #     j.reputation -= 1
            #     j.save()

            # Delete this person Acceptance votes
            # tt = Rate.objects.filter(obywatel=i.id)
            # for x in tt:
            #     print(x.obywatel.uid)
            #     x.rate=0
                # x.save()
            # tt.delete()
            Rate.objects.filter(obywatel=i.id).update(rate=0)

            # Banned person takes back all acceptance from everyone
            # for k in Uzytkownik.objects.all():
            #     if i == k:    # but not yourself
            #         continue
            #     akceptacja = Rate()
            #     akceptacja.obywatel = i
            #     akceptacja.kandydat = k
            #     akceptacja.rate = 0
            #     akceptacja.save()
            #     try:
            #         akceptacja.save()
            #         print('okokokokok')
            #     except:  # TODO: except something
            #         print('eeeeeeeeeeeeeeeeeee')
            #         continue


            send_mail(
                f'{str(request.get_host())} - Twoje konto zostało zablokowane',
                f'Witaj {i.uid.username}\nTwoje konto na {str(request.get_host())} zostało zablokowane.',
                str(settings.DEFAULT_FROM_EMAIL),
                [i.uid.email],
                fail_silently=False,
            )

            # We are not deleting user bacuse he may come back.

    l.info(f'Population: {population}. Required reputation: {required_reputation}')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request,
                             'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'obywatele/change_password.html', {'form': form})


@login_required
def profil(request):
    if request.method == 'POST':
        username = request.user.username
        return render(request, 'index.html', {'username': username})


def password_generator(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(size))
