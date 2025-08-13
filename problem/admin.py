from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea
from django.utils.html import format_html
from .models import Problem, ProblemTag, ProblemType
from choice.models import ChoiceOption


class ChoiceOptionInline(admin.TabularInline):
    """选择题选项内联编辑"""
    model = ChoiceOption
    extra = 4
    fields = ('sequence', 'content', 'is_correct')
    ordering = ('sequence',)


class ProblemAdminForm(ModelForm):
    """自定义Problem表单"""
    choice_template = CharField(
        widget=Textarea(attrs={'rows': 10, 'cols': 80}),
        required=False,
        help_text="选择题模板（当题目类型为选择题时使用）",
        initial="""请根据以下描述选择正确答案：

题目描述：
[在此输入题目描述]

选项：
A. [选项A内容]
B. [选项B内容] 
C. [选项C内容]
D. [选项D内容]

请选择正确答案。"""
    )
    
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
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表页面，添加增加选择题按钮"""
        extra_context = extra_context or {}
        extra_context['show_add_choice_button'] = True
        return super().changelist_view(request, extra_context)
    
    def response_add(self, request, obj, post_url_continue=None):
        """添加题目后的响应处理"""
        if '_addchoice' in request.POST:
            # 如果是添加选择题，重定向到选择题添加页面
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('admin:choice_choiceproblem_add'))
        return super().response_add(request, obj, post_url_continue)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('_id', 'title', 'problem_type', 'difficulty', 'is_public', 'contest')
        }),
        ('题目内容', {
            'fields': ('description', 'input_description', 'output_description', 'hint')
        }),
        ('选择题模板', {
            'fields': ('choice_template',),
            'classes': ('collapse',),
            'description': '当题目类型为选择题时，可以使用此模板快速创建题目描述'
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
    
    def get_inlines(self, request, obj):
        """根据题目类型动态显示内联编辑器"""
        if obj and obj.problem_type == ProblemType.CHOICE:
            return [ChoiceOptionInline]
        return []
    
    def get_fieldsets(self, request, obj=None):
        """根据题目类型动态调整字段集"""
        fieldsets = list(self.fieldsets)
        
        if obj and obj.problem_type == ProblemType.CHOICE:
            # 选择题类型，显示选择题模板
            fieldsets[2] = ('选择题模板', {
                'fields': ('choice_template',),
                'description': '选择题模板，可以复制到题目描述中使用'
            })
        else:
            # 编程题类型，隐藏选择题模板
            fieldsets[2] = ('选择题模板', {
                'fields': ('choice_template',),
                'classes': ('collapse',),
                'description': '当题目类型为选择题时，可以使用此模板快速创建题目描述'
            })
        
        return fieldsets
    
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