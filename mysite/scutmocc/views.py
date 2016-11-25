# coding: utf-8
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect

from mysite.settings import SECRET_KEY
from scutmocc.models import Theme, College, Board, ThemeAnswer, Dianzan, Attention, CollectTheme
from scutmocc.validation import Token
from .forms import ActivityForm, PersonalForm
from scutmocc.juncheepaginator import JuncheePaginator
import re


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
    best_theme_list = Theme.objects.filter(Legal=True).order_by('-Dz_sum', '-Zjhf_date')[:10]
    return render(request, "bbs/homepage.html", context={"best_theme_list": best_theme_list})


# display one of boards in bbs
def bbs_board(request, board_type):
    if board_type == 'activity':
        board = Board.objects.get(Board_name='a')
    elif board_type == 'question':
        board = Board.objects.get(Board_name='b')
    else:
        board = Board.objects.get(Board_name='c')

    college_list = College.objects.all()
    theme_list = board.theme_set.filter(Legal=True)
    college_type = request.GET.get('college_type')
    sort_type = request.GET.get('sort_type')

    if college_type:
        theme_list = theme_list.filter(College_type=college_type)

    if sort_type == 'popular':
        pass
    elif sort_type == 'latest':
        theme_list = theme_list.order_by('-Fb_date')
    elif sort_type == 'latest_reply':
        theme_list = theme_list.order_by('-Zjhf_date')
    elif sort_type == 'most_reply':
        theme_list = theme_list.order_by('-Hf_sum')

    page_num = request.GET.get('page_num', 1)
    paginator = JuncheePaginator(theme_list, 1)
    try:
        theme_list = paginator.page(page_num)
    except PageNotAnInteger:
        theme_list = paginator.pag(1)
    except EmptyPage:
        theme_list = paginator.pag(paginator.num_pages)

    return render(request, 'bbs/board.html',
                  context={'college_list': college_list, 'theme_list': theme_list, 'board': board, 'college_type': college_type})


# display one of themes in board
def bbs_theme(request, board_type, theme_id):
    try:
        theme_item = Theme.objects.get(pk=theme_id)
    except ObjectDoesNotExist:
        raise Http404()
    # 判断用户是否已经登录
    if request.user.is_authenticated:
        # 判断用户是否对评论点赞
        reply_list = []
        for reply_infos in theme_item.themeanswer_set.all():
            try:
                is_dianzan = Dianzan.objects.get(Fbr_Id=request.user, ThemeAnswer_Id=reply_infos).Is_Dianzan
                reply_list.append({'reply_infos': reply_infos, 'is_dianzan': is_dianzan})
            except ObjectDoesNotExist:
                reply_list.append({'reply_infos': reply_infos, 'is_dianzan': False})

        # 判断用户是否对主题点赞
        try:
            is_dianzan = Dianzan.objects.get(Fbr_Id=request.user, Theme_Id=theme_item).Is_Dianzan
        except ObjectDoesNotExist:
            is_dianzan = False

        # 判断用户是否关注主题的发表人
        try:
            is_paid = Attention.objects.get(Ox_Id=theme_item.Fbr, Fs_Id=request.user).Is_paid
        except ObjectDoesNotExist:
            is_paid = False

        # 判断用户是否收藏主题
        try:
            is_collected = CollectTheme.objects.get(Yh_Id=request.user, Theme_Id=theme_item.id).Is_Collected
        except ObjectDoesNotExist:
            is_collected = False
        return render(request, 'bbs/theme.html', {'theme_item': theme_item, 'is_dianzan': is_dianzan,
                                                  'reply_list': reply_list, 'is_paid': is_paid,
                                                  'is_collected': is_collected})

    else:
        return render(request, 'bbs/theme.html', {'theme_item': theme_item, 'is_dianzan': False,
                                                  'is_paid': False, 'is_collected': False})


# use to dianzan in bbs
# ?如果没有登录跳转到登录界面
@login_required
def bbs_dianzan(request):
    # 判断请求是否来自ajax
    if not request.is_ajax():
        raise Http404()

    dianzan_type = request.GET.get("type")
    dianzan_id = request.GET.get("id")

    if dianzan_type == "theme":
        try:
            theme_item = Theme.objects.get(pk=dianzan_id)
            # 通知主题的发表人有新的点赞
            # 更新Dianzan表的数据
            dianzan_item = Dianzan.objects.get_or_create(Fbr_Id=request.user, Theme_Id=theme_item)[0]
            # 取反
            dianzan_item.Is_Dianzan = not dianzan_item.Is_Dianzan
            dianzan_item.save()
            # 更新点赞数
            if dianzan_item.Is_Dianzan:
                theme_item.Dz_sum += 1
            else:
                theme_item.Dz_sum -= 1

            theme_item.save()
            return JsonResponse({'res': dianzan_item.Is_Dianzan, 'dz_sum': theme_item.Dz_sum})
        except Theme.DoesNotExist:
            return JsonResponse()
    elif dianzan_type == "reply":
        try:
            reply_item = ThemeAnswer.objects.get(pk=dianzan_id)
            # 通知回复的发表人有新的点赞
            # 更新Dianzan表的数据
            dianzan_item = Dianzan.objects.get_or_create(Fbr_Id=request.user, ThemeAnswer_Id=reply_item)[0]
            dianzan_item.Is_Dianzan = not dianzan_item.Is_Dianzan
            dianzan_item.save()

            # 更新点赞数
            if dianzan_item.Is_Dianzan:

                reply_item.Dz_sum += 1
            else:
                reply_item.Dz_sum -= 1

            reply_item.save()
            return JsonResponse({'res': dianzan_item.Is_Dianzan, 'dz_sum': reply_item.Dz_sum})
        except ThemeAnswer.DoesNotExist:
            return JsonResponse()


@login_required
def bbs_attention(request):
    # 判断请求是否来自ajax
    if not request.is_ajax():
        raise Http404()

    try:
        # 根据请求的ox_id获取对应的User
        ox = User.objects.get(pk=request.GET.get("ox_id"))
        # 建立关注关系
        atten = Attention.objects.get_or_create(Ox_Id=ox, Fs_Id=request.user)[0]

        atten.Is_paid = not atten.Is_paid
        atten.save()

        return JsonResponse({"paid": atten.Is_paid})
    except ObjectDoesNotExist:
        raise Http404()


@login_required
def bbs_collect_theme(request):
    if not request.is_ajax():
        raise Http404()

    try:
        # 获取主题对象
        theme = Theme.objects.get(pk=request.GET.get("theme_id"))
        # 建立收藏关系
        collect = CollectTheme.objects.get_or_create(Yh_Id=request.user, Theme_Id=theme)[0]
        collect.Is_Collected = not collect.Is_Collected
        collect.save()

        return JsonResponse({"collected": collect.Is_Collected})

    except ObjectDoesNotExist:
        raise Http404()


@login_required
def bbs_reply(request):
    # 区别回复主题还是回复评论，后台实现/不区分回复主题和评论，而是直接以@的形式
    # 正确性检测：前端非空检测;后台检测@last_name是否正确
    # 回复评论的格式 @last_name
    # 通知主题作者
    # 通知评论作者
    try:
        # 获取主题
        theme = Theme.objects.get(pk=request.POST.get("theme_id"))
        # 获取回复内容
        reply_content = request.POST.get("reply_content")
        # 检查是否有@其他人
        it = re.finditer(r'@(\w+)\s', reply_content)
        for i in it:
    except ObjectDoesNotExist:
        raise Http404()


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
