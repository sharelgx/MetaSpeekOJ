from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import json

from utils.api import APIView, validate_serializer
from account.decorators import super_admin_required, problem_permission_required
from utils.shortcuts import rand_str
from account.decorators import check_contest_permission
from contest.models import Contest
from .models import ChoiceProblem, ChoiceOption
from .serializers import ChoiceProblemSerializer, CreateChoiceProblemSerializer, EditChoiceProblemSerializer


class ChoiceProblemAPI(APIView):
    @problem_permission_required
    def get(self, request):
        """获取选择题列表或单个选择题"""
        problem_id = request.GET.get("id")
        if problem_id:
            try:
                problem = ChoiceProblem.objects.get(id=problem_id)
                return self.success(ChoiceProblemSerializer(problem).data)
            except ChoiceProblem.DoesNotExist:
                return self.error("Choice problem does not exist")

        limit = int(request.GET.get("limit", 10))
        offset = int(request.GET.get("offset", 0))
        keyword = request.GET.get("keyword", "")
        difficulty = request.GET.get("difficulty", "")
        
        problems = ChoiceProblem.objects.filter(contest__isnull=True).select_related("created_by")
        
        if keyword:
            problems = problems.filter(title__icontains=keyword)
        if difficulty:
            problems = problems.filter(difficulty=difficulty)
            
        problems = problems.order_by("-create_time")
        
        paginator = Paginator(problems, limit)
        page_number = offset // limit + 1
        page_obj = paginator.get_page(page_number)
        
        return self.success({
            "total": paginator.count,
            "results": ChoiceProblemSerializer(page_obj.object_list, many=True).data
        })

    @problem_permission_required
    @validate_serializer(CreateChoiceProblemSerializer)
    def post(self, request):
        """创建选择题"""
        data = request.data
        
        # 检查display_id是否已存在
        if ChoiceProblem.objects.filter(_id=data["display_id"], contest__isnull=True).exists():
            return self.error("Display ID already exists")
        
        with transaction.atomic():
            # 创建选择题
            choice_problem = ChoiceProblem.objects.create(
                _id=data["display_id"],
                title=data["title"],
                description=data["description"],
                difficulty=data["difficulty"],
                visible=data.get("visible", True),
                created_by=request.user,
                explanation=data.get("hint", ""),
                is_multiple=data.get("is_multiple", False)
            )
            
            # 创建选项
            for i, choice in enumerate(data["choices"]):
                is_correct = data["answer"] == chr(65 + i)  # A, B, C, D...
                ChoiceOption.objects.create(
                    problem=choice_problem,
                    content=choice["text"],
                    is_correct=is_correct,
                    sequence=i + 1
                )
        
        return self.success(ChoiceProblemSerializer(choice_problem).data)

    @problem_permission_required
    @check_contest_permission(check_type="problems")
    @validate_serializer(EditChoiceProblemSerializer)
    def put(self, request):
        """编辑选择题"""
        data = request.data
        
        try:
            choice_problem = ChoiceProblem.objects.get(id=data["id"])
        except ChoiceProblem.DoesNotExist:
            return self.error("Choice problem does not exist")
        
        with transaction.atomic():
            # 更新基本信息
            choice_problem.title = data["title"]
            choice_problem.description = data["description"]
            choice_problem.difficulty = data["difficulty"]
            choice_problem.visible = data.get("visible", True)
            choice_problem.explanation = data.get("hint", "")
            choice_problem.is_multiple = data.get("is_multiple", False)
            choice_problem.last_update_time = timezone.now()
            choice_problem.save()
            
            # 删除旧选项
            choice_problem.options.all().delete()
            
            # 创建新选项
            for i, choice in enumerate(data["choices"]):
                is_correct = data["answer"] == chr(65 + i)  # A, B, C, D...
                ChoiceOption.objects.create(
                    problem=choice_problem,
                    content=choice["text"],
                    is_correct=is_correct,
                    sequence=i + 1
                )
        
        return self.success(ChoiceProblemSerializer(choice_problem).data)

    @problem_permission_required
    @check_contest_permission(check_type="problems")
    def delete(self, request):
        """删除选择题"""
        problem_id = request.GET.get("id")
        if not problem_id:
            return self.error("Problem id is required")
        
        try:
            choice_problem = ChoiceProblem.objects.get(id=problem_id)
            choice_problem.delete()
            return self.success("Choice problem deleted successfully")
        except ChoiceProblem.DoesNotExist:
            return self.error("Choice problem does not exist")


class ContestChoiceProblemAPI(APIView):
    @problem_permission_required
    def get(self, request):
        """获取比赛选择题列表或单个选择题"""
        problem_id = request.GET.get("id")
        if problem_id:
            try:
                problem = ChoiceProblem.objects.get(id=problem_id)
                return self.success(ChoiceProblemSerializer(problem).data)
            except ChoiceProblem.DoesNotExist:
                return self.error("Choice problem does not exist")

        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Contest id is required")
        
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        
        limit = int(request.GET.get("limit", 10))
        offset = int(request.GET.get("offset", 0))
        keyword = request.GET.get("keyword", "")
        difficulty = request.GET.get("difficulty", "")
        
        problems = ChoiceProblem.objects.filter(contest=contest).select_related("created_by")
        
        if keyword:
            problems = problems.filter(title__icontains=keyword)
        if difficulty:
            problems = problems.filter(difficulty=difficulty)
            
        problems = problems.order_by("-create_time")
        
        paginator = Paginator(problems, limit)
        page_number = offset // limit + 1
        page_obj = paginator.get_page(page_number)
        
        return self.success({
            "total": paginator.count,
            "results": ChoiceProblemSerializer(page_obj.object_list, many=True).data
        })

    @problem_permission_required
    @validate_serializer(CreateChoiceProblemSerializer)
    def post(self, request):
        """创建比赛选择题"""
        data = request.data
        contest_id = data.get("contest_id")
        
        if not contest_id:
            return self.error("Contest id is required")
        
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        
        # 检查display_id是否已存在
        if ChoiceProblem.objects.filter(_id=data["display_id"], contest=contest).exists():
            return self.error("Display ID already exists in this contest")
        
        with transaction.atomic():
            # 创建选择题
            choice_problem = ChoiceProblem.objects.create(
                _id=data["display_id"],
                title=data["title"],
                description=data["description"],
                difficulty=data["difficulty"],
                visible=data.get("visible", True),
                created_by=request.user,
                explanation=data.get("hint", ""),
                is_multiple=data.get("is_multiple", False),
                contest=contest
            )
            
            # 创建选项
            for i, choice in enumerate(data["choices"]):
                is_correct = data["answer"] == chr(65 + i)  # A, B, C, D...
                ChoiceOption.objects.create(
                    problem=choice_problem,
                    content=choice["text"],
                    is_correct=is_correct,
                    sequence=i + 1
                )
        
        return self.success(ChoiceProblemSerializer(choice_problem).data)

    @problem_permission_required
    @validate_serializer(EditChoiceProblemSerializer)
    def put(self, request):
        """编辑比赛选择题"""
        data = request.data
        
        try:
            choice_problem = ChoiceProblem.objects.get(id=data["id"])
        except ChoiceProblem.DoesNotExist:
            return self.error("Choice problem does not exist")
        
        with transaction.atomic():
            # 更新基本信息
            choice_problem.title = data["title"]
            choice_problem.description = data["description"]
            choice_problem.difficulty = data["difficulty"]
            choice_problem.visible = data.get("visible", True)
            choice_problem.explanation = data.get("hint", "")
            choice_problem.is_multiple = data.get("is_multiple", False)
            choice_problem.last_update_time = timezone.now()
            choice_problem.save()
            
            # 删除旧选项
            choice_problem.options.all().delete()
            
            # 创建新选项
            for i, choice in enumerate(data["choices"]):
                is_correct = data["answer"] == chr(65 + i)  # A, B, C, D...
                ChoiceOption.objects.create(
                    problem=choice_problem,
                    content=choice["text"],
                    is_correct=is_correct,
                    sequence=i + 1
                )
        
        return self.success(ChoiceProblemSerializer(choice_problem).data)

    @problem_permission_required
    def delete(self, request):
        """删除比赛选择题"""
        problem_id = request.GET.get("id")
        if not problem_id:
            return self.error("Problem id is required")
        
        try:
            choice_problem = ChoiceProblem.objects.get(id=problem_id)
            choice_problem.delete()
            return self.success("Choice problem deleted successfully")
        except ChoiceProblem.DoesNotExist:
            return self.error("Choice problem does not exist")