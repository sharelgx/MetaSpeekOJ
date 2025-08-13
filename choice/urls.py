from django.urls import path
from . import views
from .admin_views import ChoiceProblemAPI, ContestChoiceProblemAPI

app_name = 'choice'

urlpatterns = [
    # 选择题列表
    path('', views.choice_problem_list, name='list'),
    # 展示选择题
    path('problem/<str:problem_id>/', views.show_choice_problem, name='show'),
    # 提交答案
    path('problem/<str:problem_id>/submit/', views.submit_choice_answer, name='submit'),
    # 查看结果
    path('result/<int:submit_id>/', views.show_submit_result, name='result'),
    # 创建选择题（管理员）
    path('admin/create/', views.create_choice_problem, name='create'),
    
    # 管理员API
    path('api/admin/choice_problem/', ChoiceProblemAPI.as_view(), name='admin_choice_problem_api'),
    path('api/admin/contest/choice_problem/', ContestChoiceProblemAPI.as_view(), name='admin_contest_choice_problem_api'),
]