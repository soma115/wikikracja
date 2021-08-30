from django.views.generic import DetailView, ListView
from django.conf import settings
from .models import Article
from .forms import CommentForm
from django.shortcuts import render, get_object_or_404


class ArticleView(DetailView):
    model = Article
    template_name = 'article/detail.html'


class ArticleListView(ListView):
    model = Article
    template_name = 'article/list.html'
    paginate_by = getattr(settings, 'ARTICLE_PAGINATE_BY', None)

    def get_queryset(self):
        queryset = super(ArticleListView, self).get_queryset()
        if self.request.user.is_active:
            return queryset.filter(published=True)
        else:
            return queryset.filter(published=True, public=True)


def post_detail(request, slug):
    template_name = 'post_detail.html'
    post = get_object_or_404(Article, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form})