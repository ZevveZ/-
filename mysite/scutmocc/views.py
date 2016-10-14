from django.shortcuts import render

# display the homepage


def homepage(request):
    return render(request, 'homepage/homepage.html')
git
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

