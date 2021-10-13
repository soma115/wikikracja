from elibrary.forms import UpdateBookForm
from elibrary.models import Book
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import FormView, CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
# from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from PIL import Image
import os
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404


@login_required
def add(request):
    if request.method == 'POST':
        form = UpdateBookForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.uploader = User.objects.get(username=request.user.username)
            obj.save()

            image = Image.open(obj.cover)
            image = image.resize((200, 300), Image.ANTIALIAS)
            # upload_file_name = obj.cover.file.name
            # print(upload_file_name)
            image.save('media/elibrary/' + str(obj.id) + '.png')
            obj.cover.name = 'elibrary/' + str(obj.id) + '.png'
            # form.save_m2m()  # taggit
            # os.remove(upload_file_name)  # delete original file
            obj.save()
            return redirect('elibrary:book-list')
    else:
        form = UpdateBookForm()
    return render(request, 'elibrary/add.html', {'form': form})


class BookList(LoginRequiredMixin, ListView):
    # template_name = 'elibrary/elibrary.html'

    def get_queryset(self):
        return Book.objects.all()


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    # print(request.object.id)
    # Files are not physicaly deleted. This needs to be changed
    success_url = reverse_lazy('elibrary:book-list')


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['book_list'] = Book.objects.all()

        # Previous and Next
        obj = get_object_or_404(Book, pk=self.kwargs['pk'])
        # kandydaci czy obywatele? Na razie wszyscy
        prev = Book.objects.filter(pk__lt=obj.pk).order_by('-pk').first()
        next = Book.objects.filter(pk__gt=obj.pk).order_by('pk').first()

        context['prev'] = prev
        context['next'] = next

        return context

    # success_url = reverse_lazy('elibrary:elibrary')
    queryset = Book.objects.all()

    def get_object(self):
        obj = super().get_object()
        # Record the last accessed date
        return obj


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'cover', 'file_epub', 'file_mobi', 'file_pdf']

    def form_valid(self, form):
        if form.instance.cover == "":
            form.instance.cover = 'elibrary/default.png'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('elibrary:book-detail', kwargs={'pk': self.object.pk})
