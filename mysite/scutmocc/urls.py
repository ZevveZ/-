from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^test/$', views.test, name='test'),
    url(r'^$', auth_views.login, {'template_name': 'homepage/homepage.html'}, name='homepage'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'homepage/logout.html'}, name='logout'),
    url(r'^register_person/$', views.personal_registration, name='personal_registration'),
    url(r'^register_activity/$', views.activity_registration, name='activity_registration'),
    # 修改url
    url(r'^activate/(.+)/$', views.activate, name='activate'),
    url(r'^change_password/$', auth_views.password_change, {'template_name': 'homepage/change_password.html',
                                                            'post_change_redirect': r'/scutmocc/'},
        name='password_change'),
    url(r'reset_password/$', auth_views.password_reset, {'template_name': 'homepage/reset_password.html',
                                                         'email_template_name': 'homepage/password_reset_email.html',
                                                              'subject_template_name': 'homepage/password_reset_subject.txt',
                                                         'post_reset_redirect': '/scutmocc/'},
        name='password_reset'),
    url(r'^reset_password_confirm/(?P<uidb64>[\w]*)/(?P<token>[\w-]*)/$', auth_views.password_reset_confirm, {'template_name': 'homepage/reset_password_confirm.html',
                                                                          'post_reset_redirect': '/scutmocc/'},
        name='password_reset_confirm'),
    # consider the length of \d+ latter
    url(r'^(?P<user_id>\d+)$', views.user_center, name='user_center'),
    url(r'^(?P<user_id>\d+)/subles/(?P<kind>\d+)/$', views.submit_les, name='sub_les'),
    url(r'^course/$', views.course_list, name='course_list'),
    url(r'^course/(?P<label_id>\d+)/$', views.course_detail, name='course_detail'),
    url(r'^course/(?P<label_id>\d+)/(?P<les_id>\d+)$', views.lesson_detail, name='lesson_detail'),
    url(r'^bbs/$', views.bbs_homepage, name='bbs_homepage'),
    url(r'^bbs/(?P<board_type>(?:activity|question|street))/$', views.bbs_board, name='bbs_board'),
    url(r'^bbs/(?P<board_name>(?:activity|question|street))/(?P<theme_id>\d+)$', views.bbs_theme,
        name='bbs_theme')
]
