from django.contrib.auth.models import User
from django.shortcuts import render

from scutmocc.validation import validate


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
    return render(request, 'bbs/homepage.html')


# display one of boards in bbs
def bbs_board(request, board_type):
    return render(request, 'bbs/board.html', {'board_type': board_type})


# display one of themes in board
def bbs_theme(request, board_name, theme_id):
    return render(request, 'bbs/theme.html', {'board_name': board_name, 'theme_id': theme_id})


# deal with personal registration
def personal_registration(request):
    # 前端保证此时用户不会处于登录状态
    if request.method == 'POST':
        xm = request.POST.get('xm')
        zxh = request.POST.get('zxh')
        if validate(zxh, xm):
            nickname = request.POST.get('nickname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            # 验证邮箱
            user = User.objects.create_user(zxh, email, password, last_name=xm)
            user.person.Nickname = nickname
            user.save()
        else:
            # 身份验证失败
            return render(request, template_name='homepage/register_person.html', context={'tips': 'validation_fail'})
    else:
        # 不是post方式，返回empty的注册界面
        return render(request, template_name='homepage/register_person.html')


# deal with community registration
def community_registration(request):
    pass

