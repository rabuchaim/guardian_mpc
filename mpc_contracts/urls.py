from django.urls import path
from .views import ContractCreateView, ContractListAllView, ContractListView, ContractSummaryView

urlpatterns = [
    path('create/',ContractCreateView.as_view(),name='create'),
    path('list/all/',ContractListAllView.as_view(),name='list_all'),
    path('list/',ContractListView.as_view(),name='list'),
    path('summary/',ContractSummaryView.as_view(),name='summary'),
]
