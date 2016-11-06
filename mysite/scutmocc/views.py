# coding: utf-8
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_list_or_404
from scutmocc.models import Theme

from mysite.settings import SECRET_KEY
from scutmocc.validation import Token
from .forms import ActivityForm, PersonalForm


def homepage(request):
    return render(request, 'homepage/homepage.html')


# display user center
def user_center(request, user_id):
    return render(request, 'user_center/user_center.html', {'user_id': user_id})


# display all kinds of course
def course_list(request):
    return render(request, 'course/course_list.html')


# display one kind of courses' detail
def course_detail(request, label_id):
    return render(request, 'course/course_detail.html', {'label_id': label_id})


# display one of lessons' detail
def lesson_detail(request, label_id, les_id):
    return render(request, 'course/lesson_detail.html', {'label_id': label_id, 'les_id': les_id})


# display the homepage of bbs
def bbs_homepage(request):
    best_theme_list = Theme.objects.order_by('-Dz_sum', '-Zjhf_date')[:10]
    return render(request, "bbs/homepage.html", context={"best_theme_list": best_theme_list})


# display one of boards in bbs
def bbs_board(request, board_type):
    if board_type == 'activity':
        board_type = '活动区'
        theme_list =
    elif board_type == 'question':
        board_type = '问题区'
    else:
        board_type = '话题区'

    return render(request, 'bbs/board.html', context={'board_type': board_type})


# display one of themes in board
def bbs_theme(request, board_name, theme_id):
    return render(request, 'bbs/theme.html', {'board_name': board_name, 'theme_id': theme_id})


# deal with  personal registration
m_token = Token(SECRET_KEY)


def personal_registration(request):
    # 前端保证此时用户不会处于登录状态
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        # 验证数据格式,学号和姓名,检测学号
        if form.is_valid():
            zxh = form.cleaned_data['xuehao']
            xm = form.cleaned_data['realname']
            nickname = form.cleaned_data['nickname']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(zxh, email, password, last_name=xm, is_active=False)
            user.person.Nickname = nickname
            user.save()
            # 验证邮箱
            token = m_token.generate_validation__token(user.username)
            message = '\n'.join([u'{0}，欢迎加入ScutMocc'.format(user.last_name),
                                 u'请访问链接，完成用户验证',
                                 '\\'.join(['http://127.0.0.1:8000', 'scutmocc', 'activate', token])])
            send_mail(u'注册用户验证信息', message, None, [user.email])
            return HttpResponse(u'请到注册邮箱中验证用户，有效期为1小时')
        else:
            return render(request, 'homepage/register_person.html', {'form': form})
    else:
        # 不是post方式，返回empty的注册界面
        form = PersonalForm()
        return render(request, 'homepage/register_person.html', {'form': form})


# deal with activity registration
def activity_registration(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            account = form.cleaned_data['account']
            introduce = form.cleaned_data['introduce']
            password = form.cleaned_data['password']

            user = User.objects.create_user(account, account, password, last_name=name, is_active=False)
            user.activity.Act_intro = introduce
            user.activity.Act_image = request.FILES['image']
            user.save()

            # 验证邮箱,人工验证社团用户
            message = '\n'.join([u'{0}，欢迎加入ScutMocc'.format(user.last_name),
                                u'请通过邮件回复必要的社团证明材料'])
            send_mail(u'注册用户验证信息', message, None, [user.email])
            return HttpResponse(u'请到注册邮箱中验证用户，有效期为1小时')
        else:
            return render(request, 'homepage/register_activity.html', {'form': form})
    else:
        form = ActivityForm()
        return render(request, 'homepage/register_activity.html', {'form': form})


def activate(request, token):
    username = m_token.confirm_validation_token(token)
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(u'对不起，您所验证的用户不存在，请重新注册')
    user.is_active = True
    user.save()
    # 登录用户
    login(request, user)
    return redirect(r'/scutmocc/')
