"""ADB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^movies/$', "movie.views.movies"),
    url(r'^movies/(?P<MID>[0-9]+)/$', 'movie.views.movie'),
    url(r'^users/$', "movie.views.users"),
    url(r'^login/$', "movie.views.login"),
    url(r'^comments/$', "movie.views.comments"),
    url(r'^comments/(?P<MID>[0-9]+)/$', 'movie.views.comment'),
    url(r'^rates/$', "movie.views.rates"),
    url(r'^collections/$', "movie.views.collections"),
    url(r'^collections/delete/$', "movie.views.collections_delete"),
    url(r'^collections/(?P<UID>[0-9]+)/$', 'movie.views.collection'),
    url(r'^genres/$', 'movie.views.genres'),
    url(r'^genres/(?P<GID>[0-9]+)/$', 'movie.views.genre')
]
