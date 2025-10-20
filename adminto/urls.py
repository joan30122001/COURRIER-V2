from django.urls import path
from . import views
from .views import *

app_name = "senat" 

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('chef_service/', views.chef_service, name='chef_service'),
    path('chef_depart/', views.chef_depart, name='chef_depart'),
    path('chef_arrive/', views.chef_arrive, name='chef_arrive'),
    # path(r'^(?P<id>\d+)bureau_sg/$', views.bureau_sg, name='bureau_sg'),
    path('bureau_sg/', views.bureau_sg, name='bureau_sg'),
    # path('bureau_univ/', views.bureau_univ, name='bureau_univ'),
    path('usager/', views.usager, name='usager'),
    path('search/', views.search, name='search'),
    # path('search_univ/', views.search_univ, name='search_univ'),
    path('courrier_attente/', views.courrier_attente, name='courrier_attente'),

    

    path('<int:id>', views.courrier_attente_detail, name='courrier_attente_detail'),
    path('search_chef/', views.search_chef, name='search_chef'),
    path('result_chef/', views.result_chef, name='result_chef'),
    path('/', views.list_courrier, name='list_courrier'),
    path('df/<int:pk>/', views.courrier_pdf, name="courrier_pdf"),
    # path('traited/', views.traited, name='traited'),
    # path("search/", SearchResultsList.as_view(), name="search"),
    # path("search/", SearchResultsView.as_view(), name="search_results"),
    # path('sg_record/', sg_record, name='sg_record'),
    path('envoi_email/', views.envoi_email, name='envoi_email'),

    path('scan', views.scan, name='scan'),




    path('<int:id>', views.deactivate_record, name='deactivate_record'),






    # path('inde/', views.indexs, name='indexs'),
    # path('capture/', views.capture, name='capture'),
    path('captures/', views.captures, name='captures'),
    path('capture/<int:capture_id>/download/', views.download_capture, name='download_capture'),
    path('capture_pdf/<int:capture_id>/download/', views.download_capture_pdf, name='download_capture_pdf'),





    path('search_usager/', views.search_usager, name='search_usager'),
    path('result_usager/', views.result_usager, name='result_usager'),

    path('terminer/<int:id>/', views.terminer_courrier, name='terminer_courrier'),

    # path("chatbot/", views.chatbot_page, name="chatbot"),
    # path("chatbot/ask", views.chatbot_ask, name="chatbot-ask"),  # endpoint AJAX

    # path("archives/", views.scan_list, name="scan_list"),
    # path("archives/<int:pk>/download/", views.scan_download, name="scan_download"),

    path("archives/", views.scan_list, name="scan_list"),
    path("archives/<int:pk>/preview/", views.scan_preview, name="scan_preview"),
    path("archives/<int:pk>/download/", views.scan_download, name="scan_download"),
    path("archives/<int:pk>/gemini/", views.scan_download_gemini, name="scan_download_gemini"),
]