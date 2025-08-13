from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import ChoiceProblem, ChoiceOption, ChoiceSubmission
from .forms import ChoiceAnswerForm

@login_required
def show_choice_problem(request, problem_id):
    """展示选择题"""
    problem = get_object_or_404(ChoiceProblem, _id=problem_id)
    
    # 获取选择题选项
    options = ChoiceOption.objects.filter(problem=problem).order_by('sequence')
    if not options.exists():
        messages.error(request, "这个题目没有配置选择题选项")
        return redirect('/')
        
    form = ChoiceAnswerForm(problem=problem)
    
    # 检查用户是否已经提交过
    has_submitted = ChoiceSubmission.objects.filter(
        user=request.user,
        problem=problem
    ).exists()
    
    # 获取用户的提交记录（如果有）
    user_submission = None
    if has_submitted:
        user_submission = ChoiceSubmission.objects.filter(
            user=request.user,
            problem=problem
        ).first()
    
    return render(request, 'choice/show.html', {
        'problem': problem,
        'options': options,
        'form': form,
        'has_submitted': has_submitted,
        'user_submission': user_submission
    })

@login_required
def submit_choice_answer(request, problem_id):
    """提交选择题答案"""
    problem = get_object_or_404(ChoiceProblem, _id=problem_id)
    
    # 检查是否已经提交过
    if ChoiceSubmission.objects.filter(user=request.user, problem=problem).exists():
        messages.warning(request, "您已经提交过这道题目了")
        return redirect(reverse('choice:show', args=[problem_id]))
    
    if request.method == 'POST':
        form = ChoiceAnswerForm(problem=problem, data=request.POST)
        if form.is_valid():
            selected_ids = form.cleaned_data['answers']
            if not isinstance(selected_ids, list):
                selected_ids = [selected_ids]
            
            # 获取选中的选项
            selected_options = ChoiceOption.objects.filter(id__in=selected_ids)
            
            # 判断答案是否正确
            correct_options = ChoiceOption.objects.filter(problem=problem, is_correct=True)
            is_correct = set(selected_options) == set(correct_options)
            
            # 创建提交记录
            submission = ChoiceSubmission.objects.create(
                user=request.user,
                problem=problem,
                is_correct=is_correct
            )
            
            # 添加选中的选项
            submission.selected_options.set(selected_options)
            
            # 更新题目统计信息
            problem.submission_number += 1
            if is_correct:
                problem.correct_number += 1
            problem.save()
            
            messages.success(request, f"提交成功！{'答案正确' if is_correct else '答案错误'}")
            return redirect(reverse('choice:result', args=[submission.id]))
    else:
        form = ChoiceAnswerForm(problem=problem)
        
    return render(request, 'choice/show.html', {
        'problem': problem,
        'form': form
    })

@login_required
def show_submit_result(request, submit_id):
    """展示提交结果"""
    submission = get_object_or_404(ChoiceSubmission, id=submit_id, user=request.user)
    correct_options = ChoiceOption.objects.filter(
        problem=submission.problem,
        is_correct=True
    ).order_by('sequence')
    
    return render(request, 'choice/result.html', {
        'submission': submission,
        'correct_options': correct_options,
        'problem': submission.problem
    })

@permission_required('choice.add_choiceproblem')
def create_choice_problem(request):
    """创建选择题（管理员功能）"""
    if request.method == 'POST':
        # 获取基本信息
        title = request.POST.get('title')
        description = request.POST.get('description')
        explanation = request.POST.get('explanation', '')
        difficulty = request.POST.get('difficulty', 'Low')
        is_multiple = request.POST.get('is_multiple') == 'on'
        is_public = request.POST.get('is_public') == 'on'
        visible = request.POST.get('visible') == 'on'
        
        if not title or not description:
            messages.error(request, "标题和题目描述不能为空")
            return render(request, 'choice/create.html')
        
        # 创建选择题
        problem = ChoiceProblem.objects.create(
            title=title,
            description=description,
            explanation=explanation,
            difficulty=difficulty,
            is_multiple=is_multiple,
            is_public=is_public,
            visible=visible,
            created_by=request.user
        )
        
        # 处理选项
        option_count = int(request.POST.get('option_count', 4))
        has_correct = False
        
        for i in range(1, option_count + 1):
            content = request.POST.get(f'option_{i}')
            is_correct = request.POST.get(f'correct_{i}') == 'on'
            
            if content and content.strip():
                ChoiceOption.objects.create(
                    problem=problem,
                    content=content.strip(),
                    is_correct=is_correct,
                    sequence=i
                )
                if is_correct:
                    has_correct = True
        
        if not has_correct:
            problem.delete()
            messages.error(request, "至少需要设置一个正确答案")
            return render(request, 'choice/create.html')
        
        messages.success(request, "选择题创建成功")
        return redirect(reverse('choice:show', args=[problem._id]))
    
    return render(request, 'choice/create.html')


def choice_problem_list(request):
    """选择题列表"""
    problems = ChoiceProblem.objects.filter(visible=True, is_public=True).order_by('-create_time')
    
    # 简单的分页处理
    from django.core.paginator import Paginator
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'choice/list.html', {
        'page_obj': page_obj
    })
