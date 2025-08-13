from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

class SPAView(TemplateView):
    template_name = 'index.html'
    
    def get_template_names(self):
        # 根据路径判断是管理后台还是普通用户界面
        if self.request.path.startswith('/admin'):
            return ['/home/sharelgx/OnlineJudgeFE/dist/admin/index.html']
        return ['/home/sharelgx/OnlineJudgeFE/dist/index.html']
    
    def get(self, request, *args, **kwargs):
        template_path = self.get_template_names()[0]
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/html')
        except FileNotFoundError:
            return HttpResponse('Frontend not built. Please run: cd /home/sharelgx/OnlineJudgeFE && npm run build', status=404)

urlpatterns = [
    # Django Admin
    url(r'^django-admin/', admin.site.urls),
    
    # API routes
    url(r"^api/", include("account.urls.oj")),
    url(r"^api/admin/", include("account.urls.admin")),
    url(r"^api/", include("announcement.urls.oj")),
    url(r"^api/admin/", include("announcement.urls.admin")),
    url(r"^api/", include("conf.urls.oj")),
    url(r"^api/admin/", include("conf.urls.admin")),
    url(r"^api/", include("problem.urls.oj")),
    url(r"^api/admin/", include("problem.urls.admin")),
    url(r"^api/", include("contest.urls.oj")),
    url(r"^api/admin/", include("contest.urls.admin")),
    url(r"^api/", include("submission.urls.oj")),
    url(r"^api/admin/", include("submission.urls.admin")),
    url(r"^api/admin/", include("utils.urls")),
    
    # Static files from frontend build
    url(r'^static/(?P<path>css/loader\.css)$', serve, {'document_root': '/home/sharelgx/OnlineJudgeFE/dist/static', 'show_indexes': False}, name='loader_css'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': '/home/sharelgx/OnlineJudgeFE/dist', 'show_indexes': False}),
    
    # Admin frontend routes
    url(r'^admin/.*$', SPAView.as_view(), name='admin_spa'),
    
    # Main frontend routes (catch-all for SPA)
    url(r'^.*$', SPAView.as_view(), name='spa'),
]
