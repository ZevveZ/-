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

admin.site.register(Person)
admin.site.register(LabelField)
admin.site.register(SubmitLes)
admin.site.register(CommentField)
admin.site.register(AnswerField)
admin.site.register(ChoiceLes)
admin.site.register(Board)
admin.site.register(Theme)
admin.site.register(ThemeAnswer)
admin.site.register(CollectTheme)
admin.site.register(Attention)
admin.site.register(Activity)
admin.site.register(College)

