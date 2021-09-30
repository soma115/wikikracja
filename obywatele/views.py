from django.conf import settings as s
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.messages import success, error
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.timezone import now as dzis
from django.utils.translation import ugettext_lazy as _
from random import choice
from string import ascii_letters, digits
from math import log
import logging as l
from obywatele.forms import UserForm, ProfileForm, EmailChangeForm
from obywatele.models import Uzytkownik, Rate
from django.contrib.auth.models import Group
from PIL import Image
import os

l.basicConfig(filename='wiki.log', datefmt='%d-%b-%y %H:%M:%S', format='%(asctime)s %(levelname)s %(funcName)s() %(message)s', level=l.INFO)


def population():
    try:
        population = User.objects.filter(is_active=True).count()
        return population
    except:
        pass
        l.error(f"Population zero, I don't know what to do.")


def required_reputation():
    return round(log(population()) * s.ACCEPTANCE_MULTIPLIER)

@login_required() 
def email_change(request):
    form = EmailChangeForm(request.user)
    if request.method=='POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            message = _("Your new email has been saved.")
            success(request, (message))
            return redirect('obywatele:my_profile')
        else:
            message = form.errors
            error(request, (message))
            return redirect('obywatele:my_profile')
    else:
        return render(request, 'obywatele/email_change.html', {'form':form})


@login_required
def obywatele(request):
    zliczaj_obywateli(request)
    uid = User.objects.filter(is_active=True)
    return render(request, 'obywatele/start.html', {
        'uid': uid,
        'population': population(),
        'acceptance': s.ACCEPTANCE_MULTIPLIER,
        'required_reputation': required_reputation(),
        })


@login_required
def poczekalnia(request):
    zliczaj_obywateli(request)
    uid = User.objects.filter(is_active=False)
    return render(request, 'obywatele/poczekalnia.html', {
        'uid': uid,
        'population': population(),
        'acceptance': s.ACCEPTANCE_MULTIPLIER,
        'required_reputation': required_reputation(),
        })


@login_required
def dodaj(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            # USER
            mail = user_form.cleaned_data['email']
            nick = user_form.cleaned_data['username']

            if User.objects.filter(email=mail).exists():
                # is_valid doesn't check if email exist
                message = _('Email already exist')
                error(request, (message))
                return redirect('obywatele:zaproponuj_osobe')

            else:
                # If everything is ok
                user_form.save()
                candidate = User.objects.get(username=nick)
                candidate.is_active = False
                candidate.save()

                # CANDIDATE
                candidate_profile = Uzytkownik.objects.get(id=candidate.id)
                candidate_profile.polecajacy = request.user.username
                candidate_profile.phone = profile_form.cleaned_data['phone']
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

                message = _('The new user has been saved')
                success(request, (message))
                return redirect('obywatele:poczekalnia')
        else:
            message = user_form.errors.get_json_data()['username'][0]['message']
            error(request, (message))
            return redirect('obywatele:zaproponuj_osobe')

    user_form = UserForm()
    profile_form = ProfileForm()

    return render(request, 'obywatele/dodaj.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def my_profile(request):
    pk=request.user.id
    profile = Uzytkownik.objects.get(pk=pk)
    user = User.objects.get(pk=pk)
    return render(request, 'obywatele/my_profile.html', {'profile': profile,
                                                         'user': user,
                                                         'population': population(),
                                                         'required_reputation': required_reputation(),})


@login_required
def my_assets(request):
    pk=request.user.id
    profile = Uzytkownik.objects.get(pk=pk)
    user = User.objects.get(pk=pk)
    form = ProfileForm(request.POST, request.FILES)

    if request.method == 'POST':
        if form.is_valid():
            # Remove foto: form.cleaned_data['foto'] = False
            # Add foto:  form.cleaned_data['foto'] = uplodaed_file_name.png
            if form.cleaned_data['foto'] == False:
                profile.foto = 'obywatele/anonymous.png'
            else:
                profile.foto = form.cleaned_data['foto']
            profile.phone = form.cleaned_data['phone']
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
            profile.gift = form.cleaned_data['gift']
            profile.other = form.cleaned_data['other']
            profile.save()

            if form.cleaned_data['foto']:
                image = Image.open(profile.foto)
                width, height = image.width, image.height
                dest_height = 200
                factor = height / dest_height
                new_height = round(height / factor)
                new_width = round(width / factor)
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
                image.save('media/obywatele/' + str(user.id) + '.png')
                profile.foto.name = 'obywatele/' + str(user.id) + '.png'
                os.remove(profile.foto.file.name)  # delete original file
                profile.save()

            return render(
                request,
                'obywatele/my_profile.html',
                {
                    'message': _('Changes was saved'),
                    'profile': profile,
                    'required_reputation': required_reputation(),
                }
            )
        else:  # form.is_NOT_valid():
            message = form.errors
            error(request, (message))

            return render(
                request,
                'obywatele/my_profile.html',
                {
                    'message': _('Form is not valid!'),
                    'profile': profile,
                    'required_reputation': required_reputation(),
                }
            )
    else:  # request.method != 'POST':
        form = ProfileForm(initial={  # pre-populate fields from database
            'foto': profile.foto,
            'phone': profile.phone,
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
    zliczaj_obywateli(request)
    all_assets = Uzytkownik.objects.filter(uid__is_active=True)
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

    candidate_profile = get_object_or_404(Uzytkownik, pk=pk)
    candidate_user = User.objects.get(pk=pk)
    citizen_profile = Uzytkownik.objects.get(pk=request.user.id)
    citizen_reputation = citizen_profile.reputation
    polecajacy = citizen_profile.polecajacy

    rate = Rate.objects.get_or_create(kandydat=candidate_profile, obywatel=citizen_profile)[0]

    if rate.rate == 1:
        r1 = _('positive')
    if request.GET.get('tak'):
        rate.rate = 1
        rate.save()
        return redirect('obywatele:obywatele_szczegoly', pk)

    if rate.rate == -1:
        r1 = _('negative')
    if request.GET.get('nie'):
        rate.rate = -1
        rate.save()
        return redirect('obywatele:obywatele_szczegoly', pk)

    if rate.rate == 0:
        r1 = _('neutral')
    if request.GET.get('reset'):
        rate.rate = 0
        rate.save()
        return redirect('obywatele:obywatele_szczegoly', pk)

    return render(
        request,
        'obywatele/szczegoly.html',
        {
            'b': candidate_profile,
            'd': citizen_profile,
            'tr': citizen_reputation,
            'wr': required_reputation(),
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

    # Count everyones reputation from Rate model and put it in to Uzytkownik
    for i in Uzytkownik.objects.all():

        if Rate.objects.filter(kandydat=i).exists():
            reputation = Rate.objects.filter(kandydat=i).aggregate(Sum('rate'))
            i.reputation = list(reputation.values())[0]
            # l.info(f'Candidate: {i.uid.id}; Reputation: {list(reputation.values())[0]};')
            i.save()

    # Włącz użytkowników z odpowiednio wysoką reputacją
    for i in Uzytkownik.objects.all():
        if i.reputation > required_reputation() and not i.uid.is_active:
            i.uid.is_active = True  # Uzytkownik.uid -> User

            i.uid.is_staff = True
            # Add to Editor group
            editor = Group.objects.get(name='Editor')
            editor.user_set.add(i.uid)

            password = password_generator()
            i.uid.set_password(password)
            i.data_przyjecia = dzis()
            i.uid.save()
            l.info(f'Activating user {i.uid}')
            i.save()
            
            # New person accepts automatically every other active user
            for k in Uzytkownik.objects.filter(uid__is_active=True):
                if i == k:    # but not yourself
                    continue
                obj, created = Rate.objects.update_or_create(obywatel = i, kandydat = k, defaults={'rate': '1'})

            subject = request.get_host() + ' - Twoje konto zostało włączone'
            uname = str(i.uid.username)
            uhost = str(request.get_host())
            # TODO: Tłumaczenie na angielski
            message = f'Witaj {uname}\nTwoje konto na {uhost} zostało włączone.\n\nTwój login to: {uname}\nTwoje hasło to: {password}\n\nZaloguj się tutaj: {uhost}/login/\n\nHasło możesz zmienić tutaj: {uhost}/haslo/'
            
            send_mail(subject, message, s.DEFAULT_FROM_EMAIL, [i.uid.email], fail_silently=False)

    # Blokuj użytkowników ze zbyt niską reputacją
    for i in Uzytkownik.objects.all():
        # l.info(f'Uzytkownik {i.id} reputation: {i.reputation}')
        if i.reputation < required_reputation() and i.uid.is_active:
            i.uid.is_active = False  # Uzytkownik.uid -> User
            i.uid.save()
            l.info(f'Blocking user {i.uid}')
            i.save()

            # Banned person takes back all acceptance from everyone
            Rate.objects.filter(obywatel=i.id).update(rate=0)

            send_mail(
                f'{str(request.get_host())} - Twoje konto zostało zablokowane',
                f'Witaj {i.uid.username}\nTwoje konto na {str(request.get_host())} zostało zablokowane.',
                str(s.DEFAULT_FROM_EMAIL),
                [i.uid.email],
                fail_silently=False,
            )
            # We are not deleting user bacuse he may come back.

    # l.info(f'Population: {POPULATION}. Required reputation: {REQUIRED_REPUTATION}')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            success(request,
                             'Your password was successfully updated!')
            return redirect('change_password')
        else:
            error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'obywatele/change_password.html', {'form': form})


def password_generator(size=8, chars=ascii_letters + digits):
    return ''.join(choice(chars) for i in range(size))
