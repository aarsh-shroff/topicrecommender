from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import AddressForm
from .trends import get_recommendations, related_topics, related_queries
from .models import Webpages

import pandas as pd
from pprint import pprint

# Create your views here.

def home(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('recommendations/')
    else:
        form = AddressForm()
    return render(request, 'index.html', {'form': form})

def recommendations(request):
    webpages = Webpages.objects.all().order_by("-id")[0]
    webpages_list = [webpages.url1, webpages.url2, webpages.url3, webpages.url4, webpages.url5]
    recommendations = get_recommendations(webpages_list)
    top_queries = list()
    rising_queries = list()

    for i in range(len(recommendations[0])):
        kw = (next(iter(recommendations[0][i])))
        if recommendations[0][i][kw]['top'] is not None:
            top_queries.append(recommendations[0][i][kw]['top'].to_html())
        if recommendations[0][i][kw]['rising'] is not None:
            rising_queries.append(recommendations[0][i][kw]['rising'].to_html())
    
    '''
    for i in range(len(recommendations[1])):
        kw = (next(iter(recommendations[1][i])))
        if recommendations[1][i][kw]['top'] is not None:
            top_topics.append(recommendations[1][i][kw]['top'].to_html(columns=['topic_title', 'topic_type', 'formattedValue']))
        if recommendations[1][i][kw]['rising'] is not None:
            rising_topics.append(recommendations[1][i][kw]['rising'].to_html(columns=['topic_title', 'topic_type', 'formattedValue']))
    '''

    context_dict = {'top_queries': top_queries, 
                    'rising_queries': rising_queries,
                    'keywords': recommendations[2]}
    
    return render(request, 'recommendations.html', context_dict)