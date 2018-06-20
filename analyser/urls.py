from django.conf.urls import url, include
from django.contrib import admin

from analyser import views

urlpatterns = [
    url(r'^$', views.get_labels,name='get_labels'),

]
