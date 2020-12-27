from elibrary.forms import UploadFileForm
from elibrary.models import Ebook
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
# from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required


class IndexView(generic.ListView):
    template_name = 'elibrary/elibrary.html'

    def get_queryset(self):
        return Ebook.objects.all()


@login_required
def add(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            form = form.save(commit=False)
            form.uploader = User.objects.get(username=request.user.username)
            form.title = str(
                request.FILES.getlist('file')).rsplit(
                    ':')[1].replace('>]', '').rsplit(
                        '(')[0].strip().replace('[', '').replace(']', '')
            form.save()
            return redirect('elibrary:elibrary')
    else:
        form = UploadFileForm()
    return render(request, 'elibrary/add.html', {'form': form})


class BookDelete(DeleteView):
    model = Ebook
    # TODO: Files are not physicaly deleted.
    success_url = reverse_lazy('elibrary:elibrary')
