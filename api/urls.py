# api/urls.py (새로 만드는 파일)

from django.urls import path
from . import views  # views.py 파일 import

urlpatterns = [
    # POST /api/analyze/ 요청을 views.py의 AnalyzeView 가 처리
    path('analyze/', views.AnalyzeView.as_view(), name='analyze'),
]