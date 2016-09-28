from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    # consider the length of \d+ latter
    url(r'^(?P<user_id>\d+)$', views.user_center, name='user_center'),
    url(r'^course/$', views.course_list, name='course_list'),
    url(r'^course/(?P<label_id>\d+)/$', views.course_detail, name='course_detail'),
    url(r'^course/(?P<label_id>\d+)/(?P<les_id>\d+)$', views.lesson_detail, name='lesson_detail'),
    url(r'^bbs/$', views.bbs_homepage, name='bbs_homepage'),
    url(r'^bbs/(?P<board_type>(?:activity|question|street))/$', views.bbs_board, name='bbs_board'),
    url(r'^bbs/(?P<board_name>(?:activity|question|street))/(?P<theme_id>\d+)$', views.bbs_theme,
        name='bbs_theme')
]
