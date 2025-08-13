from django import forms
from .models import ChoiceProblem, ChoiceOption, ChoiceSubmission

class ChoiceAnswerForm(forms.Form):
    """选择题答题表单"""
    def __init__(self, problem, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.problem = problem
        options = ChoiceOption.objects.filter(problem=problem).order_by('sequence')
        
        # 根据题目设置判断是单选还是多选
        self.is_multiple = problem.is_multiple
        
        if self.is_multiple:
            # 多选题使用MultipleChoiceField
            self.fields['answers'] = forms.MultipleChoiceField(
                choices=[(opt.id, opt.content) for opt in options],
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                label="请选择答案（多选）",
                required=True
            )
        else:
            # 单选题使用ChoiceField
            self.fields['answers'] = forms.ChoiceField(
                choices=[(opt.id, opt.content) for opt in options],
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                label="请选择答案（单选）",
                required=True
            )
    
    def clean_answers(self):
        """验证答案"""
        selected_ids = self.cleaned_data['answers']
        if not isinstance(selected_ids, list):
            selected_ids = [selected_ids]
            
        # 验证选项是否存在
        valid_options = ChoiceOption.objects.filter(
            problem=self.problem, 
            id__in=selected_ids
        )
        
        if len(valid_options) != len(selected_ids):
            raise forms.ValidationError("选择的选项无效")
            
        return selected_ids


class ChoiceProblemForm(forms.ModelForm):
    """选择题创建/编辑表单"""
    
    class Meta:
        model = ChoiceProblem
        fields = ['title', 'description', 'explanation', 'difficulty', 'is_multiple', 'is_public', 'visible']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入题目标题'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': '请输入题目描述'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入题目解析（可选）'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'is_multiple': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': '题目标题',
            'description': '题目描述',
            'explanation': '题目解析',
            'difficulty': '难度等级',
            'is_multiple': '是否为多选题',
            'is_public': '是否公开',
            'visible': '是否可见',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置默认值
        if not self.instance.pk:
            self.fields['is_public'].initial = True
            self.fields['visible'].initial = True