from django.shortcuts import render
from django.views.generic import ListView
from .models import News

# Create your views here.

class NewsListView(ListView):
    model = News
    template_name = "news/news_list.html"
    context_object_name = "news_list"
    paginate_by = 10

    def get_queryset(self):
        return News.objects.filter(
            is_published=True,
        ).order_by("-created_at")