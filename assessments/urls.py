from django.urls import path
from .views import dashboard_data, save_final_score

urlpatterns = [
    path("dashboard-data/", dashboard_data, name="dashboard_data"),
    path("save_final_score/", save_final_score, name="save_final_score"),
]
