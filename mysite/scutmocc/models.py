from django.db import models


#   Lession repo
class LabelField(models.Model):
    Lession={
        ('a', '项目'),
        ('b', '理论课'),
        ('c', '技能')
    }
    Label_Kind = models.CharField(max_length=1, choices=Lession);
    Label_Name = models.CharField(max_length=50);


# College Field


class CollegeField(models.Model):
    College_Name = models.CharField(max_length=30);
    College_Account = models.IntegerField();


# Submit Lession


class SubmitLes(models.Model):
    Person_Id = models.ForeignKey(User);
    Label_Id = models.ForeignKey(LabelField);
    Les_Name = models.CharField(max_length=60);
    Les_Plan = models.CharField(max_length=200);
    Les_Time = models.IntegerField();
    Les_Way = models.CharField(max_length=200);
    Les_Price = models.IntegerField();
    Les_Merge = models.IntegerField();  # 0～3 社团 0~10
    Les_Another = models.CharField(max_length=150);
    Les_Term = models.IntegerField();
    Les_Next = models.DateField();
    Les_Status = models.BooleanField();


# Comment Lession


class CommentField(models.Model):
    Les_Id = models.ForeignKey(SubmitLes);
    Person_Id = models.ForeignKey(User);
    Comment = models.CharField(max_length=500);


# Answer Lession


class AnswerField(models.Model):
    Comment_Id = models.ForeignKey(CommentField);
    Person_Id = models.ForeignKey(User);
    Answer = models.CharField(max_length=500);

    #   Relation of Choice Lession


class ChoiceLes(models.Model):
    Les_Id = models.ForeignKey(SubmitLes);
    Person = models.ForeignKey(User);
    Ch_Date = models.DateField();
    End = models.BooleanField();
    Les_Assess = models.CharField(max_length=500, null=True);

    #   Board


class Board(models.Model):
    Field = {
        ('a', '活动区'),
        ('b', '问题区'),
        ('c', '话题区')
    }
    Board_type = models.CharField(max_length=1,choices=Field);
    Gg_content = models.CharField(200);
    Jrzt_sum = models.IntegerField();
    Zrzt_sum = models.IntegerField();
    Zt_sum = models.IntegerField();

    #  Theme


class Theme(models.Model):
    Content = models.CharField();
    Title = models.CharField();
    Fb_date = models.DateTimeField();
    Zjhf_date = models.DateTimeField();
    Zd = models.BooleanField()
    Dz_sum = models.IntegerField();
    Board_type = models.ForeignKey(Board);
    Fbr_id = models.ForeignKey(User);
    Yd_sum = models.IntegerField();
    Legal = models.BooleanField();
    Sc_sum = models.IntegerField();

    # BBS answer


class ThemeAnswer(models.Model):
    Hfr_Id = models.ForeignKey(User);
    Lc_no = models.IntegerField();
    Fb_date = models.DateTimeField();
    Theme_Id = models.ForeignKey(Theme);
    Dz_sum = models.IntegerField();
    Legal = models.BooleanField();

    # Collect Theme


class CollectTheme(models.Model):
    Yh_Id = models.ForeignKey(User);
    Theme_Id = models.ForeignKey(Theme);

    # Pay attention


class Attention(models):
    Fs_Id = models.ForeignKey(User);
    Ox_Id = models.ForeignKey(User);
