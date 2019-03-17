from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.models import User
from obywatele.forms import ObywatelForm
from obywatele.models import Uzytkownik, AkceptacjaOsoby
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
import random
import string
from django.utils.timezone import now as dzis

WYMAGANY_PROCENT_AKCEPTACJI = 0.2	# it is a %. It will be used later like this: 
									# required_acceptance = population * WYMAGANY_PROCENT_AKCEPTACJI

def obywatele(request):
	zliczaj_obywateli(request)
	uid = User.objects.filter(is_active=True)
	# TODO: dodać datę przyjęcia do szczegółów każdego użytkownika
	return render(request, 'obywatele/start.html', {'uid': uid})


def poczekalnia(request):
	zliczaj_obywateli(request)
	uid = User.objects.filter(is_active=False)
	return render(request, 'obywatele/poczekalnia.html', {'uid': uid})


def dodaj(request):
	if request.method == 'POST':
		form = ObywatelForm(request.POST)
		if form.is_valid():
			mail = form.cleaned_data['email']
			nick = form.cleaned_data['username']

			if User.objects.filter(email=mail).exists():
				# is_valid doesn't check if email exist
				wynik = 'Email już istnieje'
				return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

			else:
				# If everything is ok
				form.save()
				nowa_osoba = User.objects.get(username=nick)
				nowa_osoba.is_active = False
				nowy_w_uzytkownikach = Uzytkownik.objects.get(id=nowa_osoba.id)
				nowy_w_uzytkownikach.polecajacy = request.user.username
				# nowa_osoba.data_zgloszenia doesn't make sense becauese date_joined 
				# in auth_user already exist.
				# nowa_osoba.data_zgloszenia nie ma sensu bo już istnieje date_joined 
				# w auth_user
				nowa_osoba.save()
				nowy_w_uzytkownikach.save()

				# Since you proposed new person, you probably also want to acceppt him
				dawca = Uzytkownik.objects.get(pk=request.user.id)

				glos = AkceptacjaOsoby()
				nowy_w_uzytkownikach.reputacja += 1
				glos.kandydat = nowy_w_uzytkownikach
				glos.obywatel = dawca
				glos.save()
				nowy_w_uzytkownikach.save()

				wynik = 'Nowy użytkownik został zapisany'
				return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })
		else:
			wynik = form.errors
			return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

	form = ObywatelForm()
	return render(request, 'obywatele/dodaj.html', {'form': form})


def obywatele_szczegoly(request, pk):
	dawca = Uzytkownik.objects.get(pk=request.user.id)
	biorca = get_object_or_404(Uzytkownik, pk=pk)

	if request.GET.get('tak'):
		# Accept pk
		# Zaakceptuj pk

		glos = AkceptacjaOsoby()

		# Check if this person already accepted candidate
		# Sprawdźmy czy ten użytkownik polubił już tego kandydata
		jest_glos = AkceptacjaOsoby.objects.filter(obywatel=request.user.id, kandydat=pk)
		if jest_glos:
			wynik = 'Już wcześniej nadałeś reputację użytkownikowi ' + str(User.objects.get(pk=pk))
			return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })
		else:
			biorca.reputacja += 1
			glos.kandydat = biorca
			glos.obywatel = dawca
			glos.save()
			biorca.save()
			wynik = 'Ok, nadałeś użytkownikowi ' + str(User.objects.get(pk=pk)) + ' punkt reputacji.'
			return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

	if request.GET.get('nie'):
		# Recall acceptance from pk
		# Odbierz akceptację od pk

		glos = AkceptacjaOsoby()

		# Check if this person already accepted candidate
		# Sprawdźmy czy ten użytkownik polubił już tego kandydata
		jest_glos = AkceptacjaOsoby.objects.filter(obywatel=request.user.id, kandydat=pk)

		if jest_glos:
			glos = AkceptacjaOsoby.objects.filter(obywatel=request.user.id, kandydat=pk)
			biorca.reputacja -= 1

			AkceptacjaOsoby.objects.get(obywatel=request.user.id, kandydat=pk).delete()
			biorca.save()
			wynik = 'Ok, odebrałeś użytkownikowi ' + str(User.objects.get(pk=pk)) + ' punkt reputacji.'
		else:
			wynik = 'Już odebrałeś wcześniej temu użytkownikowi reputację.'
		return render(request, 'obywatele/zapisane.html', {'wynik': wynik, })

	populacja = User.objects.filter(is_active=True).count()
	print('populacja:',populacja)
	wymagana_rep = int(populacja * WYMAGANY_PROCENT_AKCEPTACJI)
	twoja_rep = dawca.reputacja
	
	return render(request, 'obywatele/szczegoly.html', {'b': biorca, 'd': dawca, 'tr': twoja_rep, 'wr': wymagana_rep})


def zliczaj_obywateli(request): # TODO: zamienić na obiekt z metodą: "podaj obecną populację".
	'''Citizens should be accepted by voting but banned with by 
	judge - if they break the law. This is only temporal solution for small comunities.'''
	# Potrzebne w 'obywatele_szczegóły'
	populacja = User.objects.filter(is_active=True).count()
	wymagana_reputacja = int(populacja * WYMAGANY_PROCENT_AKCEPTACJI)

	akceptacja = AkceptacjaOsoby()

	# Blokuj użytkowników ze zbyt niską reputacją
	for i in Uzytkownik.objects.all():

		if i.reputacja < wymagana_reputacja and i.uid.is_active:
			i.uid.is_active = False
			i.uid.save()
			i.save()

			# Odbierz wszystkim pozostałym 1 punkt reputacji
			for j in Uzytkownik.objects.all():
				print(j.uid)
				j.reputacja -= 1
				j.save()

			# Delete this person Acceptance votes
			AkceptacjaOsoby.objects.filter(obywatel=i.id).delete()

			send_mail(
				str(request.get_host())+' - Twoje konto zostało zablokowane',
				'Witaj ' + i.uid.username + '\nTwoje konto na '+str(request.get_host())+' zostało zablokowane.',
				'from@example.com',
				[i.uid.email],
				fail_silently=False,
			)

			# Also delete this person User and Uzytkownik instances.
			Uzytkownik.objects.get(id=i.id).delete()
			User.objects.get(id=i.id).delete()

	# Włącz użytkowników z odpowiednio wysoką reputacją
	for i in Uzytkownik.objects.all():
		if i.reputacja > wymagana_reputacja and not i.uid.is_active:
			i.uid.is_active = True
			password = password_generator()
			i.uid.set_password(password)
			i.data_przyjecia = dzis()
			i.uid.save()
			i.save()

			# Nadaj wszystkim pozostałym 1 punkt reputacji
			for j in Uzytkownik.objects.all():
				if i != j:
					j.reputacja += 1
					j.save()
			
			# Give automatially every person Acceptance
			# New person accepts automatically everyone
			for k in Uzytkownik.objects.all():
				if i == k:	# but not yourself
					continue
				akceptacja = AkceptacjaOsoby()
				akceptacja.obywatel = i
				akceptacja.kandydat = k
				try:
					akceptacja.save()
				except:
					continue

			send_mail(
				str(request.get_host())+' - Twoje konto zostało włączone',
				'Witaj '+i.uid.username+'\nTwoje konto na '+str(request.get_host())+' zostało włączone.\n\nTwoje hasło: '+password+'\n\nHasło możesz zmienić po zalogowaniu w swoim profilu: '+request.get_host()+'/haslo/',
				'from@example.com',  # TODO: should be configurable in secrets.py
				[i.uid.email],
				fail_silently=False,
			)


def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('change_password')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'obywatele/change_password.html', {'form': form})


def profil(request):
	if request.method == 'POST':
		username = request.user.username
		return render(request, 'index.html', {'username': username})


def password_generator(size=8, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for i in range(size))
