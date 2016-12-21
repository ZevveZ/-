# coding: utf-8
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
import string
from mysite.settings import SECRET_KEY
from scutmocc.models import Theme, College, Board, ThemeAnswer, Dianzan, Attention, CollectTheme, SubmitLes, LabelField, \
    ChoiceLes
from scutmocc.validation import Token
from .forms import ActivityForm, PersonalForm, SublesForm
from scutmocc.juncheepaginator import JuncheePaginator
import re


def homepage(request):
    xiangmu = SubmitLes.objects.filter(Les_Kind='a')
    lesson = SubmitLes.objects.filter(Les_Kind='b')
    shizhan = SubmitLes.objects.filter(Les_Kind='c')
    x_length = xiangmu.counet()
    l_length = lesson.count()
    s_length = shizhan.count()
    if x_length > 5:
        xiangmu = xiangmu.all()[x_length-5:x_length]
    else:
        xiangmu = xiangmu.all()
    if l_length > 5:
        lesson = lesson.all()[l_length-5:l_length]
    else:
        lesson = lesson.all()
    if s_length > 5:
        shizhan = shizhan.all()[s_length-5:s_length]
    else:
        shizhan = shizhan.all()
    return render(request, 'homepage/homepage.html')


def search(request):
    if request.method == 'POST':
        key = request.POST.get('keyword')
        try:
            lessons = SubmitLes.objects.filter(Les_Name__icontains=key).all()
        except ObjectDoesNotExist:
            return HttpResponse("很抱歉没有找到相关课程")
        return render(request, 'homepage/search_result.html', {'lessons': lessons})
    else:
        return HttpResponse('页面不存在')


# display user center
def user_center(request, user_id):
    user = User.objects.get(id=user_id)
    try:
        lessons = SubmitLes.objects.filter(Person_Id=user).all()
        students = {}
        for lesson in lessons:
            try:
                student = ChoiceLes.objects.filter(Les_Id=lesson).all()
                students[lesson.id] = student
            except ObjectDoesNotExist:
                pass
    except ObjectDoesNotExist:
        lessons = None

    try:
        myles = ChoiceLes.objects.filter(Person=user).all()
    except ObjectDoesNotExist:
        myles = None

    return render(request, 'user_center/user_center.html', {'lessons': lessons, 'students': students, 'myles': myles})


def my_page(request, user_id):
    print("redirect")
    return redirect('user_center', user_id=user_id)


@login_required
def submit_les(request, user_id, kind):
    print("here")
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        print("post")
        form = SublesForm(request.POST)
        if form.is_valid():
            print("valid")
            name = form.cleaned_data['name']
            labelname = form.cleaned_data['label']
            label = LabelField.objects.get(Label_Name=labelname)
            intro = form.cleaned_data['intro']
            time = form.cleaned_data['time']
            price = form .cleaned_data['price']
            if form.cleaned_data['merge'] is not None:
                merge = form.cleaned_data['merge']
            else:
                merge = 1
            another = form.cleaned_data['another']
            SubmitLes.objects.create(Person_Id=user, Label_Id=label, Les_Name=name, Les_Intro=intro, Les_Time=time,
                                     Les_Price=price, Les_Merge=merge, Les_Another=another)

            return redirect('user_center', user_id=user_id)
        else:
            print("else")
            return render(request, 'user_center/subles.html', {'lesform': form, 'kind': kind})
    else:
        form = SublesForm()
        print("form")
        return render(request, 'user_center/subles.html', {'lesform': form, 'kind': kind})


def my_course(request, user_id, les_id):
    lesson = SubmitLes.objects.get(id=les_id)
    data = {'name': lesson.Les_Name, 'label': lesson.Label_Id.Label_Name,
            'intro': lesson.Les_Intro, 'time': lesson.Les_Time, 'price': lesson.Les_Price,
            'merge': lesson.Les_Merge, 'another': lesson.Les_Another
            }

    if request.method == 'POST':
        form = SublesForm(request.POST, initial=data)
        if form.is_valid():
            if form.has_changed():
                print("valid")
                name = form.cleaned_data['name']
                labelname = form.cleaned_data['label']
                label = LabelField.objects.get(Label_Name=labelname)
                intro = form.cleaned_data['intro']
                time = form.cleaned_data['time']
                price = form.cleaned_data['price']
                merge = form.cleaned_data['merge']
                another = form.cleaned_data['another']
                lesson.Les_Name= name
                lesson.Label_Id= label
                lesson.Les_Intro= intro
                lesson.Les_Time = time
                lesson.Les_Price= price
                lesson.Les_Merge= merge
                lesson.Les_Another = another
                lesson.save()
            return redirect('user_center', user_id=user_id)
        else:
            return render(request, 'user_center/my_course.html', {'course': form, 'id': les_id})
    else:
        form = SublesForm(data)
        return render(request, 'user_center/my_course.html', {'course': form, 'id': les_id})


# display all kinds of course
def course_list(request, direction, labeler, character):
    if direction:
        if direction == 'd':
            courses = SubmitLes.objects.filter(Les_Status=True)
        else:
            courses = SubmitLes.objects.filter(Les_Status=True).filter(Les_Kind=direction)
    else:
        courses = SubmitLes.objects.all()
        direction = 'd'
    if labeler:
        if labeler == '0':
            courses = courses.all()
        else:
            labeler = int(labeler)
            label = LabelField.objects.get(id=labeler)
            courses = courses.filter(Label_Id=label).all()
    else:
        labeler = 0
    if character:
        if character == '0':
            courses = courses.all()
        if character == '1':
            courses == courses.filter(Person_Id__activity__isnull=True).all()
        if character == '2':
            courses = courses.filter(Person_Id__person__isnull=True).all()
    else:
        character = '0'
    labels = LabelField.objects.all()
    page_num = request.GET.get('page_num', 1)
    paginator = JuncheePaginator(courses, 2)
    try:
        courses = paginator.page(page_num)
    except PageNotAnInteger:
        courses = paginator.pag(1)
    except EmptyPage:
        courses = paginator.pag(paginator.num_pages)
    return render(request, 'course/course_list.html', context={'courses': courses, 'labels': labels,
                                                               'direction': direction, 'labeler': labeler,
                                                               'character': character})


def course_detail(request, direction, labeler, character):
    return render(request, 'course/course_detail.html')


# display one of lessons' detail
@login_required
def lesson_detail(request, les_id):
    lesson = SubmitLes.objects.get(id=les_id)
    if request.method == 'POST':
        tel = request.POST.get('tel')
        uid = request.POST.get('uid')
        if lesson.Les_Pnum > 0:
            student = User.objects.get(id=uid)
            ChoiceLes.objects.create(Les_Id=lesson, Person=student, Contact=tel, End=False)
            lesson.Les_Pnum = lesson.Les_Merge - 1
            lesson.save()
            return HttpResponse("订课成功，请前往个人中心查看")
        else:
            return HttpResponse("很遗憾课程人数已满")
    else:
        return render(request, 'course/lesson_detail.html', {'lesson': lesson})

        # remain = request.Get.get('remain')
    # if remain:
    #     if lesson.Les_Pnum > 0:
    #         student = User.objects.get(id=remain)
    #         ChoiceLes.objects.create(Les_Id=les_id, Person=student, Contact=student.email, End=False)
    #         lesson.Les_Pnum = lesson.Les_Merge - 1;
    #         return HttpResponse("订课成功，请前往个人中心查看")
    #     else:
    #         return HttpResponse("很遗憾课程人数已满")
    # else:
    #     return render(request, 'course/lesson_detail.html', {'lesson': lesson})


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
        # 更新阅读数
        theme_item.Yd_sum +=1
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


# 将板块名字转换为对应的url
board_name_to_url = {'a': 'activity', 'b': 'question', 'c': 'topic'}


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
                # ----
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
        # ----
        # 更新主题信息
        theme.Zjhf_date = themeanswer.Fb_date
        theme.Hf_sum += 1
        theme.Zjhfr = request.user
        theme.save()
        # 重定向到主题页面
        return redirect('bbs_theme', board_type=board_name_to_url[theme.Board_type.Board_name], theme_id=theme.id)
    except ObjectDoesNotExist:
        # 主题不存在
        raise Http404()


@login_required
def bbs_reply_delete(request, reply_id):
    try:
        # 删除回复
        reply = ThemeAnswer.objects.get(pk=reply_id)
        reply.delete()
        # 更新回复数
        reply.Theme_Id.Hf_sum -= 1
        reply.Theme_Id.save()
        return redirect('bbs_theme', board_type=board_name_to_url[reply.Theme_Id.Board_type.Board_name], theme_id=reply.Theme_Id.id)
    except ObjectDoesNotExist:
        raise Http404()


@login_required
def bbs_theme_edit(request):
    return render(request, 'bbs/theme_edit.html')


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
