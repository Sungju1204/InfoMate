# api/urls.py (새로 만드는 파일)

from django.urls import path
from . import views  # views.py 파일 import


urlpatterns = [
    # ★★★ /api/analyze (슬래시 없이) 요청을 views.AnalyzeView로 연결합니다. ★★★
    path('analyze', views.AnalyzeView.as_view(), name='analyze_api'),
]