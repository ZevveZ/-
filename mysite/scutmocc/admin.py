# Register your models here.

from django.contrib import admin

from scutmocc.models import AnswerField
from scutmocc.models import Attention
from scutmocc.models import Board
from scutmocc.models import ChoiceLes
from scutmocc.models import CollectTheme
from scutmocc.models import CommentField
from scutmocc.models import LabelField
from scutmocc.models import Person, Activity, College
from scutmocc.models import SubmitLes
from scutmocc.models import Theme
from scutmocc.models import ThemeAnswer


# 将Theme后台的textarea替换为tinymce
class ThemeAdmin(admin.ModelAdmin):
    class Media:
        js = ('/media/scutmocc/js/jquery-3.1.0.min.js', '/media/bbs/js/tinymce/tinymce.min.js',
              '/media/bbs/js/tinymce/jquery.tinymce.min.js', '/media/bbs/js/textarea_to_tinymce.js')


admin.site.register(Person)
admin.site.register(LabelField)
admin.site.register(SubmitLes)
admin.site.register(CommentField)
admin.site.register(AnswerField)
admin.site.register(ChoiceLes)
admin.site.register(Board)
# 绑定自定义的ThemeAdmin
admin.site.register(Theme, ThemeAdmin)
admin.site.register(ThemeAnswer)
admin.site.register(CollectTheme)
admin.site.register(Attention)
admin.site.register(Activity)
admin.site.register(College)

