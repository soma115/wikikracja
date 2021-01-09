from django.shortcuts import redirect

message = _("Your new email has been saved.")
messages.success(request, (message))
return redirect('obywatele:obywatele_szczegoly', pk)
return redirect('chat')

return render(request, 'chat:add_room', {'form': form})

message = user_form.errors.get_json_data()['username'][0]['message']

<a class="btn btn-default fr-rounded fr-small btn-sm" href="{% url 'obywatele:obywatele' %}">{% trans 'Citizens' %}</a>

{% trans "" %}

