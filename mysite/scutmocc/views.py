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
from django.views.decorators.csrf import csrf_exempt

from mysite.settings import SECRET_KEY
from scutmocc.models import Theme, College, Board, ThemeAnswer, Dianzan, Attention, CollectTheme, SubmitLes, \
    Notification
from scutmocc.validation import Token
from .forms import ActivityForm, PersonalForm, SublesForm
from scutmocc.juncheepaginator import JuncheePaginator
import re
from PIL import Image
import time
import datetime
from django.core.urlresolvers import reverse
from mysite import settings


def homepage(request):
    return render(request, 'homepage/homepage.html')


# display user center
@login_required
def user_center(request, user_id):
    # 无论地址中的user_id等于多少，都返回当前登录用户的个人中心
    return render(request, 'user_center/user_center.html', {'user_id': request.user.id, 'user_name': request.user.last_name})


@login_required
def user_center_bbs(request, user_id):
    # 允许查看其他用户的信息
    user = User.objects.get(pk=user_id)
    # 获取用户的合法主题
    theme_list = Theme.objects.filter(Fbr=user, Legal=True).all()
    # 获取用户的回复
    reply_list = ThemeAnswer.objects.filter(Hfr_Id=user).all()
    # 获取用户的收藏
    collect_list = CollectTheme.objects.filter(Yh_Id=user).all()
    # 获取用户的正在关注
    following = Attention.objects.filter(Fs_Id=user).all()
    # 获取关注登录用户的列表
    follower = Attention.objects.filter(Ox_Id=user).all()
    return render(request, 'user_center/bbs.html', {'theme_list': theme_list,
                                                    'reply_list': reply_list,
                                                    'collect_list': collect_list,
                                                    'following': following,
                                                    'follower': follower,
                                                    'user_name': user.last_name})


@login_required
def submit_les(request, user_id, kind):
    # 无论地址中的user_id等于多少，都返回当前登录用户的个人中心
    user = request.user
    if request.method == 'POST':
        lesson = SubmitLes.objects.get(Person_Id=user)
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
    best_theme_list = Theme.objects.filter(Legal=True, Dz_sum__gte=1).order_by('-Dz_sum', '-Zjhf_date')[:10]
    return render(request, "bbs/homepage.html", context={"best_theme_list": best_theme_list})


# display one of boards in bbs
def bbs_board(request, board_type):
    if board_type == 'activity':
        board = Board.objects.get(Board_name='活动区')
    elif board_type == 'question':
        board = Board.objects.get(Board_name='问题区')
    else:
        board = Board.objects.get(Board_name='话题区')

    college_list = College.objects.all()
    theme_list = board.theme_set.filter(Legal=True)
    college_type = request.GET.get('college_type')
    sort_type = request.GET.get('sort_type')

    # 获取统计信息
    today = datetime.date.today()
    yesterday = today + datetime.timedelta(days=-1)
    total_theme = theme_list.count()
    today_theme = theme_list.filter(Fb_date__year=today.year, Fb_date__month=today.month,
                                    Fb_date__day=today.day).count()

    yesterday_theme = theme_list.filter(Fb_date__year=yesterday.year, Fb_date__month=yesterday.month,
                                        Fb_date__day=yesterday.day).count()

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
    paginator = JuncheePaginator(theme_list, 10)
    try:
        theme_list = paginator.page(page_num)
    except PageNotAnInteger:
        theme_list = paginator.pag(1)
    except EmptyPage:
        theme_list = paginator.pag(paginator.num_pages)

    return render(request, 'bbs/board.html',
                  context={'college_list': college_list, 'theme_list': theme_list, 'board': board,
                           'college_type': college_type, 'total_theme': total_theme, 'today_theme': today_theme,
                           'yesterday_theme': yesterday_theme})


# display one of themes in board
def bbs_theme(request, board_type, theme_id):
    try:
        theme_item = Theme.objects.get(pk=theme_id)
        # 更新阅读数
        theme_item.Yd_sum += 1
        theme_item.save()
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
        return render(request, 'bbs/theme_display.html', {'theme_item': theme_item, 'is_dianzan': is_dianzan,
                                                  'reply_list': reply_list, 'is_paid': is_paid,
                                                  'is_collected': is_collected})

    else:
        return render(request, 'bbs/theme_display.html', {'theme_item': theme_item, 'is_dianzan': False,
                                                  'is_paid': False, 'is_collected': False})


# 将板块名字转换为对应的url
board_name_to_url = {'活动区': 'activity', '问题区': 'question', '话题区': 'topic'}


# use to dianzan in bbs
dianzan_theme_template = '在你的主题<a href="' + settings.HOST + 'scutmocc/bbs/%(board_type)s/%(theme_id)d">%(title)s</a>点赞了你'
dianzan_reply_template = '在主题<a href="' + settings.HOST + 'scutmocc/bbs/%(board_type)s/%(theme_id)d%(reply_count)s">%(title)s</a>点赞了你的回复'


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

            # 更新Dianzan表的数据
            try:
                dianzan_item = Dianzan.objects.get(Fbr_Id=request.user, Theme_Id=theme_item)
            except ObjectDoesNotExist:
                dianzan_item = Dianzan.objects.create(Fbr_Id=request.user, Theme_Id=theme_item)
                # 第一次点赞时才发送通知
                # 创建通知,通知主题的发表人有新的点赞
                Notification.objects.create(sender=request.user, receiver=theme_item.Fbr,
                                            message=dianzan_theme_template % {
                                                'board_type': board_name_to_url[theme_item.Board_type.Board_name],
                                                'theme_id': theme_item.id, 'title': theme_item.Title})

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
            print("reply_item")
            # 更新Dianzan表的数据
            try:
                dianzan_item = Dianzan.objects.get(Fbr_Id=request.user, ThemeAnswer_Id=reply_item)
            except ObjectDoesNotExist:
                dianzan_item = Dianzan.objects.create(Fbr_Id=request.user, ThemeAnswer_Id=reply_item)
                # 第一次点赞时才发送通知
                # 创建通知，通知回复的发表人有新的点赞
                Notification.objects.create(sender=request.user, receiver=reply_item.Hfr_Id,
                                            message=dianzan_reply_template % {'board_type': board_name_to_url[
                                                reply_item.Theme_Id.Board_type.Board_name],
                                                                              'theme_id': reply_item.Theme_Id.id,
                                                                              'title': reply_item.Theme_Id.Title,
                                                                              'reply_count': request.GET.get('reply_count')})
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


attention_template = '关注了你'


@login_required
def bbs_attention(request):
    # 判断请求是否来自ajax
    if not request.is_ajax():
        raise Http404()

    try:
        # 根据请求的ox_id获取对应的User
        ox = User.objects.get(pk=request.GET.get("ox_id"))
        # 建立关注关系
        try:
            atten = Attention.objects.get(Ox_Id=ox, Fs_Id=request.user)
        except ObjectDoesNotExist:
            atten = Attention.objects.create(Ox_Id=ox, Fs_Id=request.user)
            # 只有在第一次关注时才发送通知
            Notification.objects.create(sender=request.user, receiver=ox, message=attention_template)

        atten.Is_paid = not atten.Is_paid
        atten.save()
        return JsonResponse({"paid": atten.Is_paid})
    except ObjectDoesNotExist:
        raise Http404()


collect_notify_template = '收藏了你的主题<a href="' + settings.HOST + 'scutmocc/bbs/%(board_type)s/%(theme_id)d">%(title)s</a>'


@login_required
def bbs_collect_theme(request):
    if not request.is_ajax():
        raise Http404()

    try:
        # 获取主题对象
        theme = Theme.objects.get(pk=request.GET.get("theme_id"))
        # 建立收藏关系
        try:
            collect = CollectTheme.objects.get(Yh_Id=request.user, Theme_Id=theme)
        except ObjectDoesNotExist:
            collect = CollectTheme.objects.create(Yh_Id=request.user, Theme_Id=theme)
            # 第一次收藏主题时才发送通知
            Notification.objects.create(sender=request.user, receiver=theme.Fbr,
                                        message=collect_notify_template % {'board_type': board_name_to_url[theme.Board_type.Board_name],
                                                                           'theme_id': theme.id,
                                                                           'title': theme.Title})

        collect.Is_Collected = not collect.Is_Collected
        collect.save()

        return JsonResponse({"collected": collect.Is_Collected})

    except ObjectDoesNotExist:
        raise Http404()


reply_notify_template = '回复了你的主题<a href="' + settings.HOST + 'scutmocc/bbs/%(board_type)s/%(theme_id)d#%(reply_count)d">%(title)s</a>'
mention_notify_template = '在主题<a href="' + settings.HOST + 'scutmocc/bbs/%(board_type)s/%(theme_id)d#%(reply_count)d">%(title)s</a>的回复中提到了你'


@login_required
def bbs_reply(request):
    # 不区别回复主题还是回复评论
    # 正确性检测：前端非空检测;后台检测@last_name是否正确
    # 回复评论的格式 @last_name
    # 通知主题作者
    # 通知评论作者
    try:
        # 获取主题
        theme = Theme.objects.get(pk=request.POST.get("theme_id"))
        # 获取回复的原始内容
        raw_content = request.POST.get("reply_content")
        # display_content被加工成能够显示在前端
        display_content = raw_content

        # 检查是否有@其他人
        it = re.finditer(r'@(\w+)\s', raw_content)
        for i in it:
            try:
                mentioned_user = User.objects.get(last_name=i.group(1))
                # 发送通知给被@的用户
                Notification.objects.create(sender=request.user, receiver=mentioned_user,
                                            message=mention_notify_template % {'board_type': board_name_to_url[theme.Board_type.Board_name],
                                                                               'theme_id': theme.id,
                                                                               'title': theme.Title,
                                                                               'reply_count': theme.themeanswer_set.count()})
                # 对存在的用户在回复内容中进行链接标记,注意用户的last_name不会再修改
                # 添加标记<a href="某个用户中心">用户的last_name</a>
                display_content = display_content.replace(i.group(),
                                                          r'!(a href="%d"!)@%s!(/a!)&nbsp;' % (mentioned_user.id, i.group(1)))
            except ObjectDoesNotExist:
                # @的用户不存在时当做普通文本
                pass

        # 保存回复
        themeanswer = ThemeAnswer.objects.create(Hfr_Id=request.user, Theme_Id=theme, raw_content=raw_content, display_content=display_content)
        # 通知主题的作者
        Notification.objects.create(sender=request.user, receiver=theme.Fbr,
                                    message=reply_notify_template % {'board_type': board_name_to_url[theme.Board_type.Board_name],
                                                                     'theme_id': theme.id,
                                                                     'title': theme.Title,
                                                                     'reply_count': theme.themeanswer_set.count()})
        # 更新主题信息
        theme.Zjhf_date = themeanswer.Fb_date
        theme.Hf_sum += 1
        theme.Zjhfr = request.user
        theme.save()
        # 重定向到主题页面
        return render(request, 'template/jump.html', {'message': '回复成功', 'href': theme.Board_type.href + '/' + str(theme.id)})
    except ObjectDoesNotExist:
        # 主题不存在
        raise Http404()


@login_required
def bbs_reply_delete(request, reply_id):
    try:
        reply = ThemeAnswer.objects.get(pk=reply_id)
        # 判断当前用户是否是回复的发表人
        if reply.Hfr_Id != request.user:
            # 当前用户不是回复的发表人
            return redirect('bbs_homepage')
        reply.delete()
        # 更新回复数
        reply.Theme_Id.Hf_sum -= 1
        reply.Theme_Id.save()
        return render(request, 'template/jump.html', {'message': '删除成功', 'href': reply.Theme_Id.Board_type.href + '/' + str(reply.Theme_Id.id)})
    except ObjectDoesNotExist:
        raise Http404()


@login_required
def bbs_theme_delete(request, theme_id):
    # 判断当前用户是否是主题的发表人
    theme = Theme.objects.get(pk=theme_id)
    if theme.Fbr != request.user:
        # 当前用户不是主题的发表人
        return redirect('bbs_homepage')
    # 当前用户是主题的发表人
    # 删除主题
    theme.delete()
    return render(request, 'template/jump.html', {'message': '删除成功', 'href': reverse(bbs_homepage)})


@login_required
def bbs_theme_edit(request, theme_id):
    # 判断是创建主题还是编辑主题
    if theme_id == '':
        # 创建主题
        college_list = College.objects.all()
        return render(request, 'bbs/theme_edit.html', {'college_list': college_list})
    else:
        # 编辑主题
        # 判断主题是否存在
        theme = Theme.objects.get(id=theme_id)
        # 判断主题的作者是否是当前用户
        if theme.Fbr != request.user:
            # 重定向到论坛首页
            return redirect('bbs_homepage')
        else:
            # 装入数据
            college_list = College.objects.all()
            return render(request, 'bbs/theme_edit.html', {'theme': theme, 'college_list': college_list})


@login_required
def bbs_theme_save(request, theme_id):
    # 判断是创建主题还是更新主题
    if theme_id == '':
        # 创建主题
        fresh_theme = Theme.objects.create(Content=request.POST.get('content'), Title=request.POST.get('title'),
                                           Zjhfr=request.user,
                                           Board_type=Board.objects.get(Board_name=request.POST.get('board_name')),
                                           Fbr=request.user, College_type=College.objects.get(College_Name=request.POST.get('college_name')))
        # 用户发帖数加一
        # request.user.Fb_sum += 1
        # request.user.save()
    else:
        # 更新主题
        fresh_theme = Theme.objects.get(pk=theme_id)
        if fresh_theme.Fbr != request.user:
            # 当前用户不是主题的发表人
            return redirect('bbs_homepage')
        # 更新主题的内容、标题、版块类型、学院、最近回复人、最近回复日期
        fresh_theme.Content = request.POST.get('content')
        fresh_theme.Title = request.POST.get('title')
        fresh_theme.Board_type = Board.objects.get(Board_name=request.POST.get('board_name'))
        fresh_theme.College_type = College.objects.get(College_Name=request.POST.get('college_name'))
        fresh_theme.save()

    # 重定向到该主题页面
    return render(request, 'template/jump.html', {'message': '保存成功', 'href': fresh_theme.Board_type.href + '/' + str(fresh_theme.id)})


@login_required
@csrf_exempt
def bbs_image_upload(request):
    # 检查是否是post请求
    if request.method == 'POST':
        image = request.FILES['file']
        if image:
            image_head = str(request.user.id) + str(time.time()).split('.')[0]
            image_tail = str(image).split('.')[-1]
            image_name = image_head + '.' + image_tail
            img = Image.open(image)
            img.save('media/bbs/theme/' + image_name)
            return JsonResponse({'location': image_name})
        else:
            raise Http404()
    else:
        raise Http404()


@login_required
def bbs_notification_display(request):
    notify_list = Notification.objects.filter(receiver=request.user)
    notify_list.update(fresh=False)
    return render(request, 'bbs/notification.html', {'notify_list': notify_list})


@login_required
def bbs_notification_delete(request):
    Notification.objects.filter(receiver=request.user).delete()
    return render(request, 'template/jump.html', {'message': '清除成功', 'href': reverse(bbs_notification_display)})


@login_required
def bbs_notification_check(request):
    # 检查是否是ajax请求
    if not request.is_ajax():
        raise Http404()
    return JsonResponse({'unread': Notification.objects.filter(receiver=request.user, fresh=True).count()})

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
                                 '\\'.join([settings.HOST, 'scutmocc', 'activate', token])])
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
