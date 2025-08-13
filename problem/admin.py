from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html
from .models import Problem, ProblemTag, ProblemType


class ProblemAdminForm(ModelForm):
    """自定义Problem表单"""
    
    class Meta:
        model = Problem
        fields = '__all__'


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    form = ProblemAdminForm
    list_display = ('_id', 'title', 'problem_type', 'difficulty', 'is_public', 'create_time')
    list_filter = ('problem_type', 'difficulty', 'is_public', 'rule_type')
    search_fields = ('_id', 'title')
    readonly_fields = ('create_time', 'last_update_time')
    

    
    fieldsets = (
        ('基本信息', {
            'fields': ('_id', 'title', 'problem_type', 'difficulty', 'is_public', 'contest')
        }),
        ('题目内容', {
            'fields': ('description', 'input_description', 'output_description', 'hint')
        }),

        ('测试用例', {
            'fields': ('samples', 'test_case_id', 'test_case_score')
        }),
        ('限制设置', {
            'fields': ('time_limit', 'memory_limit', 'languages', 'template', 'io_mode')
        }),
        ('特殊判题', {
            'fields': ('spj', 'spj_language', 'spj_code', 'spj_version', 'spj_compile_ok'),
            'classes': ('collapse',)
        }),
        ('其他设置', {
            'fields': ('rule_type', 'visible', 'tags', 'source', 'total_score', 'share_submission')
        }),
        ('统计信息', {
            'fields': ('submission_number', 'accepted_number', 'statistic_info', 'create_time', 'last_update_time'),
            'classes': ('collapse',)
        })
    )
    
    inlines = []
    

    
    def save_model(self, request, obj, form, change):
        """保存时设置创建者"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        js = ('admin/js/problem_admin.js',)
        css = {
            'all': ('admin/css/problem_admin.css',)
        }


@admin.register(ProblemTag)
class ProblemTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)