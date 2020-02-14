from django.urls import re_path
from django.urls import path
from duckduckgo import views

app_name = "duckduckgo"

urlpatterns = [
        # path('recommendation/', views.recommendations, name='product_list'),

        path("wiki/", views.wikianswer, name='wikianswer')

]
