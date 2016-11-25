# coding: utf-8
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect

from mysite.settings import SECRET_KEY
from scutmocc.models import Activity, SubmitLes
from scutmocc.validation import Token
from .forms import ActivityForm, PersonalForm, SublesForm


def homepage(request):
    return render(request, 'homepage/homepage.html')


# display user center
def user_center(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, 'user_center/user_center.html', {'user_id': user.id, 'user_name': user.last_name})


def submit_les(request, user_id, kind):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        lesson = SubmitLes(Person_Id=user_id)
        form = SublesForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
        else:
            render(request, 'user_center/subles.html', {'form': form, 'kind': kind})
    else:
        form = SublesForm()
        return render(request, 'user_center/subles.html', {'form': form, 'kind': kind})


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
    return render(request, 'bbs/homepage.html')


# display one of boards in bbs
def bbs_board(request, board_type):
    return render(request, 'bbs/board.html', {'board_type': board_type})


# display one of themes in board
def bbs_theme(request, board_name, theme_id):
    return render(request, 'bbs/theme.html', {'board_name': board_name, 'theme_id': theme_id})


#test
def test(request):
    return render(request, 'homepage/test.html')


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
