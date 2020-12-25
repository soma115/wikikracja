from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.models import User
from obywatele.forms import UserForm, ProfileForm
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

# Above 0.7 second person requires 2 points of acceptance which is a paradox.
ACCEPTANCE_MULTIPLIER = 0.7  


@login_required
def obywatele(request):
    zliczaj_obywateli(request)  # TODO: show pupulation on page Obywatele
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
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # USER
            mail = user_form.cleaned_data['email']
            nick = user_form.cleaned_data['username']

            if User.objects.filter(email=mail).exists():
                # is_valid doesn't check if email exist
                wynik = 'Email już istnieje'
                return render(request,
                              'obywatele/zapisane.html',
                              {'wynik': wynik, })

            else:
                # If everything is ok
                user_form.save()
                candidate = User.objects.get(username=nick)
                candidate.is_active = False
                candidate.save()

                # CANDIDATE
                candidate_profile = Uzytkownik.objects.get(id=candidate.id)
                candidate_profile.polecajacy = request.user.username
                candidate_profile.responsibilities = profile_form.cleaned_data['responsibilities']
                candidate_profile.city = profile_form.cleaned_data['city']
                candidate_profile.hobby = profile_form.cleaned_data['hobby']
                candidate_profile.skills = profile_form.cleaned_data['skills']
                candidate_profile.knowledge = profile_form.cleaned_data['knowledge']
                candidate_profile.want_to_learn = profile_form.cleaned_data['want_to_learn']
                candidate_profile.business = profile_form.cleaned_data['business']
                candidate_profile.job = profile_form.cleaned_data['job']
                candidate_profile.fb = profile_form.cleaned_data['fb']
                candidate_profile.other = profile_form.cleaned_data['other']

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
            wynik = user_form.errors
            return render(request,
                          'obywatele/zapisane.html',
                          {'wynik': wynik, })

    user_form = UserForm()
    profile_form = ProfileForm()

    return render(request, 'obywatele/dodaj.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def my_profile(request):
    pk=request.user.id
    profile = Uzytkownik.objects.get(pk=pk)
    user = User.objects.get(pk=pk)
    population = User.objects.filter(is_active=True).count()
    required_reputation = round(log(population) * ACCEPTANCE_MULTIPLIER)
    return render(request, 'obywatele/my_profile.html', {'profile': profile, 'user': user, 'population': population, 'required_reputation': required_reputation,})


@login_required
def my_assets(request):
    pk=request.user.id
    profile = Uzytkownik.objects.get(pk=pk)
    user = User.objects.get(pk=pk)
    population = User.objects.filter(is_active=True).count()
    required_reputation = round(log(population) * ACCEPTANCE_MULTIPLIER)
    form = ProfileForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            profile.responsibilities = form.cleaned_data['responsibilities']
            profile.city = form.cleaned_data['city']
            profile.hobby = form.cleaned_data['hobby']
            profile.to_give_away = form.cleaned_data['to_give_away']
            profile.to_borrow = form.cleaned_data['to_borrow']
            profile.for_sale = form.cleaned_data['for_sale']
            profile.i_need = form.cleaned_data['i_need']
            profile.skills = form.cleaned_data['skills']
            profile.knowledge = form.cleaned_data['knowledge']
            profile.want_to_learn = form.cleaned_data['want_to_learn']
            profile.business = form.cleaned_data['business']
            profile.job = form.cleaned_data['job']
            profile.fb = form.cleaned_data['fb']
            profile.fb = form.cleaned_data['other']
            profile.save()

            return render(
                request,
                'obywatele/my_profile.html',
                {
                    'message': _('Changes was saved'),
                    'profile': profile,
                    'required_reputation': required_reputation,
                    # 'form': form,
                }
            )
        else:  # form.is_NOT_valid():
            wynik = form.errors
            return render(
                request,
                'obywatele/my_profile.html',
                {
                    'message': _('Form is not valid!'),
                    'profile': profile,
                    'required_reputation': required_reputation,
                    # 'form': form,
                }
            )
    else:  # request.method != 'POST':
        form = ProfileForm(initial={  # pre-populate fields from database
            'responsibilities': profile.responsibilities,
            'city': profile.city,
            'hobby': profile.hobby,
            'to_give_away': profile.to_give_away,
            'to_borrow': profile.to_borrow,
            'for_sale': profile.for_sale,
            'i_need': profile.i_need,
            'skills': profile.skills,
            'knowledge': profile.knowledge,
            'want_to_learn': profile.want_to_learn,
            'business': profile.business,
            'job': profile.job,
            'fb': profile.fb,
            'other': profile.other,
            }
        )

        return render(
            request,
            'obywatele/my_assets.html',
            {
                'user': user,
                'profile': profile,
                'form': form,
            }
        )


@login_required
def assets(request):
    all_assets = Uzytkownik.objects.filter(uid__is_active=True).exclude(
                                responsibilities__isnull=True,
                                city__isnull=True,
                                hobby__isnull=True,
                                to_give_away__isnull=True,
                                to_borrow__isnull=True,
                                for_sale__isnull=True,
                                i_need__isnull=True,
                                skills__isnull=True,
                                knowledge__isnull=True,
                                want_to_learn__isnull=True,
                                business__isnull=True,
                                job__isnull=True,
                                fb__isnull=True,
                                other__isnull=True,
                                )
    return render(
        request,
        'obywatele/assets.html',
        {
            'all_assets': all_assets
        },
    )


@login_required
def obywatele_szczegoly(request, pk):
    '''
    -[x] There has to be a table relating user and new person. This table is needed because vote for person may be withdrawn at some point. So there are 3 states:
      1. Candidate is positive
      2. Candidate is neutral (not clicked, default)
      3. Candidate is negative
    3 states are needed because:
      - this is a fact, those 3 states really exist
      - but most importantly: it should be possible to take reputation away - even if somebody did not give reputation to that person before.
    -[x] Reputation should be calculated from Rate table relating citizen and candidate.
    -[x] Counter should NOT be zeroed out if person drop below required reputation.
    -[x] New person increase population so also increase reputation requirements for existing citizens. Therefore every time new person is accepted - every other old member should have his reputation increased autmatically. And vice versa - if somebody is banned - everyone else should loose one point of reputation from banned person.
    '''

    citizen = Uzytkownik.objects.get(pk=request.user.id)

    candidate_profile = get_object_or_404(Uzytkownik, pk=pk)
    candidate = str(User.objects.get(pk=pk))

    population = User.objects.filter(is_active=True).count()
    required_reputation = round(log(population) * ACCEPTANCE_MULTIPLIER)
    citizen_reputation = citizen.reputation

    polecajacy = citizen.polecajacy

    rate = Rate.objects.get_or_create(kandydat=candidate_profile, obywatel=citizen)[0]

    if rate.rate == 1:
        r1 = _('positive')
    if request.GET.get('tak'):
        rate.rate = 1
        rate.save()
        wynik = str(_('Your relationship to the user ')) + candidate + str(_(' is positive'))
        return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

    if rate.rate == -1:
        r1 = _('negative')
    if request.GET.get('nie'):
        rate.rate = -1
        rate.save()
        wynik = str(_('Your relationship to the user ')) + candidate + str(_(' is negative'))
        return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

    if rate.rate == 0:
        r1 = _('neutral')
    if request.GET.get('reset'):
        rate.rate = 0
        rate.save()
        wynik = str(_('Your relationship to the user ')) + candidate + str(_(' is neutral'))
        return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

    return render(
        request,
        'obywatele/szczegoly.html',
        {
            'b': candidate_profile,
            'd': citizen,
            'tr': citizen_reputation,
            'wr': required_reputation,
            'rate': r1,
            'p': polecajacy
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

    # Be careful changing this formula - people rarely acctepting each other.
    required_reputation = round(log(population) * ACCEPTANCE_MULTIPLIER)

    # Count everyones reputation from Rate model and put it in to Uzytkownik
    for i in Uzytkownik.objects.all():

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
            
            # New person accepts automatically every other active user
            for k in Uzytkownik.objects.filter(uid__is_active=True):  # TODO: tylko aktywnych userów
                if i == k:    # but not yourself
                    continue
                obj, created = Rate.objects.update_or_create(obywatel = i, kandydat = k, defaults={'rate': '1'})

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

            # Banned person takes back all acceptance from everyone
            Rate.objects.filter(obywatel=i.id).update(rate=0)

            send_mail(
                f'{str(request.get_host())} - Twoje konto zostało zablokowane',
                f'Witaj {i.uid.username}\nTwoje konto na {str(request.get_host())} zostało zablokowane.',
                str(settings.DEFAULT_FROM_EMAIL),
                [i.uid.email],
                fail_silently=False,
            )
            # We are not deleting user bacuse he may come back.

    l.info(f'Population: {population}. Required reputation: {required_reputation}')


@login_required
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


def password_generator(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(size))
