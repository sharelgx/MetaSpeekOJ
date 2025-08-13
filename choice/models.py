from django.db import models
from django.conf import settings
from account.models import User
from contest.models import Contest
from utils.models import RichTextField
from utils.constants import Choices


class ChoiceDifficulty(object):
    High = "High"
    Mid = "Mid"
    Low = "Low"


class ChoiceProblem(models.Model):
    """独立的选择题模型"""
    # display ID
    _id = models.TextField(db_index=True)
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE)
    # for contest problem
    is_public = models.BooleanField(default=False)
    title = models.TextField("题目标题")
    # 题干 - 使用富文本编辑器
    description = RichTextField("题干")
    # 解析 - 使用富文本编辑器
    explanation = RichTextField("解析", null=True, blank=True)
    
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)
    difficulty = models.TextField("难度")
    
    # 选择题特有字段
    is_multiple = models.BooleanField("是否多选题", default=False)
    
    # 统计信息
    submission_number = models.BigIntegerField(default=0)
    correct_number = models.BigIntegerField(default=0)
    
    class Meta:
        db_table = "choice_problem"
        unique_together = (("_id", "contest"),)
        ordering = ("create_time",)
        verbose_name = "选择题"
        verbose_name_plural = "选择题"
    
    def __str__(self):
        return self.title
    
    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])
    
    def add_correct_number(self):
        self.correct_number = models.F("correct_number") + 1
        self.save(update_fields=["correct_number"])


class ChoiceOption(models.Model):
    """选择题选项模型"""
    problem = models.ForeignKey(ChoiceProblem, on_delete=models.CASCADE, related_name='options')
    content = RichTextField("选项内容")
    is_correct = models.BooleanField("是否正确答案", default=False)
    sequence = models.IntegerField("显示顺序")
    
    class Meta:
        ordering = ['sequence']
        verbose_name = "选择题选项"
        verbose_name_plural = "选择题选项"
    
    def __str__(self):
        return f"{self.problem.title} - 选项{self.sequence}"


class ChoiceSubmission(models.Model):
    """选择题提交记录模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='choice_submissions')
    problem = models.ForeignKey(ChoiceProblem, on_delete=models.CASCADE, related_name='submissions')
    selected_options = models.ManyToManyField(ChoiceOption, related_name='submissions')
    is_correct = models.BooleanField("是否正确", default=False)
    submit_time = models.DateTimeField("提交时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "选择题提交"
        verbose_name_plural = "选择题提交"
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title}"
