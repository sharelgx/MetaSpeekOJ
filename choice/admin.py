from django.contrib import admin
from .models import ChoiceProblem, ChoiceOption, ChoiceSubmission


class ChoiceOptionInline(admin.TabularInline):
    """选择题选项内联编辑"""
    model = ChoiceOption
    extra = 4
    fields = ('sequence', 'content', 'is_correct')
    ordering = ('sequence',)


@admin.register(ChoiceProblem)
class ChoiceProblemAdmin(admin.ModelAdmin):
    list_display = ('_id', 'title', 'difficulty', 'is_multiple', 'visible', 'submission_number', 'correct_number', 'create_time')
    list_filter = ('difficulty', 'is_multiple', 'visible', 'is_public', 'create_time')
    search_fields = ('_id', 'title', 'description')
    readonly_fields = ('create_time', 'last_update_time', 'submission_number', 'correct_number')
    inlines = [ChoiceOptionInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('_id', 'title', 'difficulty', 'is_multiple', 'visible', 'is_public')
        }),
        ('题目内容', {
            'fields': ('description', 'explanation')
        }),
        ('竞赛设置', {
            'fields': ('contest',),
            'classes': ('collapse',)
        }),
        ('统计信息', {
            'fields': ('submission_number', 'correct_number', 'create_time', 'last_update_time'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ChoiceOption)
class ChoiceOptionAdmin(admin.ModelAdmin):
    list_display = ('problem', 'get_content_preview', 'is_correct', 'sequence')
    list_filter = ('is_correct', 'problem__difficulty')
    search_fields = ('content', 'problem__title')
    ordering = ('problem', 'sequence')
    
    def get_content_preview(self, obj):
        """获取选项内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_content_preview.short_description = '选项内容'


@admin.register(ChoiceSubmission)
class ChoiceSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'is_correct', 'submit_time')
    list_filter = ('is_correct', 'submit_time', 'problem__difficulty')
    search_fields = ('user__username', 'problem__title')
    readonly_fields = ('submit_time',)
    
    def has_add_permission(self, request):
        """禁止手动添加提交记录"""
        return False
