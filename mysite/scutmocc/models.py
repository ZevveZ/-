from django.contrib.auth.models import PermissionsMixin, User
from django.db import models

# Create your models here.


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Nickname = models.CharField(max_length=10)
    College = models.CharField(max_length=20)
    Sex = models.NullBooleanField(null=True)
    Signature = models.CharField(max_length=100, null=True)
    Fb_sum = models.IntegerField(default=0)
    Hf_sum = models.IntegerField(default=0)
    Gz_sum = models.IntegerField(default=0)
    Bgz_sum = models.IntegerField(default=0)
    Sc_sum = models.IntegerField(default=0)
    Rank = models.IntegerField(default=0)

    def __str__(self):
        return self.user


def update_person(sender, instance, created, **kwargs):
    if created:
        person = Person()
        person.user = instance
        person.save()
    else:
        instance.person.save()


models.signals.post_save.connect(update_person, sender=User)
# # Lesson repo
# class LabelField(models.Model):
#     Lesson = {
#         ('a', '项目'),
#         ('b', '理论课'),
#         ('c', '技能')
#     }
#     Label_Kind = models.CharField(max_length=1, choices=Lesson)
#     Label_Name = models.CharField(max_length=50)
#
#
# # College Field
#
#
# class CollegeField(models.Model):
#     College_Name = models.CharField(max_length=30)
#     College_Account = models.IntegerField()
#
#
# # Submit Lesson
#
#
# class SubmitLes(models.Model):
#     Person_Id = models.ForeignKey(MyUser)
#     Label_Id = models.ForeignKey(LabelField)
#     Les_Name = models.CharField(max_length=60)
#     Les_Plan = models.CharField(max_length=200)
#     Les_Time = models.IntegerField()
#     Les_Way = models.CharField(max_length=200)
#     Les_Price = models.IntegerField()
#     Les_Merge = models.IntegerField() # 0～3 社团 0~10
#     Les_Another = models.CharField(max_length=150)
#     Les_Term = models.IntegerField()
#     Les_Next = models.DateField()
#     Les_Status = models.BooleanField()
#
#
# # Comment Lesson
#
#
# class CommentField(models.Model):
#     Les_Id = models.ForeignKey(SubmitLes)
#     Person_Id = models.ForeignKey(MyUser)
#     Comment = models.CharField(max_length=500)
#
#
# # Answer Lesson
#
#
# class AnswerField(models.Model):
#     Comment_Id = models.ForeignKey(CommentField)
#     Person_Id = models.ForeignKey(MyUser)
#     Answer = models.CharField(max_length=500)
#
#     #   Relation of Choice Lesson
#
#
# class ChoiceLes(models.Model):
#     Les_Id = models.ForeignKey(SubmitLes)
#     Person = models.ForeignKey(MyUser)
#     Ch_Date = models.DateField()
#     End = models.BooleanField()
#     Les_Assess = models.CharField(max_length=500, null=True)
#
#     #   Board
#
#
# class Board(models.Model):
#     Field = {
#         ('a', '活动区'),
#         ('b', '问题区'),
#         ('c', '话题区')
#     }
#     Board_type = models.CharField(max_length=1, choices=Field)
#     Gg_content = models.CharField(200)
#     Jrzt_sum = models.IntegerField()
#     Zrzt_sum = models.IntegerField()
#     Zt_sum = models.IntegerField()
#
#     #  Theme
#
#
# class Theme(models.Model):
#     Content = models.CharField()
#     Title = models.CharField()
#     Fb_date = models.DateTimeField()
#     Zjhf_date = models.DateTimeField()
#     Zd = models.BooleanField()
#     Dz_sum = models.IntegerField()
#     Board_type = models.ForeignKey(Board)
#     Fbr_id = models.ForeignKey(MyUser)
#     Yd_sum = models.IntegerField()
#     Legal = models.BooleanField()
#     Sc_sum = models.IntegerField()
#
#     # BBS answer
#
#
# class ThemeAnswer(models.Model):
#     Hfr_Id = models.ForeignKey(MyUser)
#     Lc_no = models.IntegerField()
#     Fb_date = models.DateTimeField()
#     Theme_Id = models.ForeignKey(Theme)
#     Dz_sum = models.IntegerField()
#     Legal = models.BooleanField()
#
#     # Collect Theme
#
#
# class CollectTheme(models.Model):
#     Yh_Id = models.ForeignKey(MyUser)
#     Theme_Id = models.ForeignKey(Theme)
#
#     # Pay attention
#
#
# class Attention(models):
#     Fs_Id = models.ForeignKey(MyUser)
#     Ox_Id = models.ForeignKey(MyUser)
