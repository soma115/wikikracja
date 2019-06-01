from elibrary.forms import UploadFileForm
from elibrary.models import Ebook
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.views import generic
# from django.core.files.storage import FileSystemStorage

# def index(request):
# 	ebooks = Ebook.objects.all()
# 	# dodać X przy książce, której jestem uploaderem
# 	return render(request, 'elibrary/all.html', {'ebooks': ebooks})


class IndexView(generic.ListView):
    template_name = 'elibrary/index.html'

    def get_queryset(self):
        # return super().get_queryset()
        return Ebook.objects.all()


# pierwotny
# def add(request):
# 	if request.method == 'POST':
# 		form = UploadFileForm(request.POST, request.FILES)

# 		if form.is_valid():
# 			form = form.save(commit=False)
# 			form.uploader = User.objects.get(username=request.user)
# 			form.title = str(request.FILES.getlist('file')).rsplit(':')[1].replace('>]', '').rsplit('(')[0].strip().replace('[', '').replace(']', '')
# 			form.save()
# 			return redirect('elibrary:index')
# 	else:
# 		form = UploadFileForm()
# 	return render(request, 'elibrary/add.html', {'form': form})


# def add(request):
# 	context = {}
# 	if request.method == 'POST':
# 		uploaded_file = request.FILES['document']
# 		fs = FileSystemStorage()
# 		name = fs.save(uploaded_file.name, uploaded_file)
# 		context['url'] = fs.url(name)
# 	return render(request, 'elibrary/add.html', context)


def add(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)

		if form.is_valid():
			form = form.save(commit=False)
			form.uploader = User.objects.get(username=request.user.username)
			form.title = str(request.FILES.getlist('file')).rsplit(':')[1].replace('>]', '').rsplit('(')[0].strip().replace('[', '').replace(']', '')
			form.save()
			return redirect('elibrary:index')
	else:
		form = UploadFileForm()
	return render(request, 'elibrary/add.html', {'form': form})


class BookDelete(DeleteView):
	model = Ebook
	success_url = reverse_lazy('elibrary:index')


# def delete(request, pk):
# 	Ebook.object.get(pk=pk).delete()
