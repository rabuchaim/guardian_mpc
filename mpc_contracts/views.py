import math
from .serializers import ContractSerializer
from .models import Contract, Parcel
from .filters import ContractFilter
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

class ContractCreateView(generics.CreateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    
    def create(self,request,*args,**kwargs):
        try:
            serializer = self.get_serializer(data=request.data,many=isinstance(request.data,list))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        except ValidationError as ERR:
            return Response({"error":str(ERR)},status=status.HTTP_400_BAD_REQUEST)
        
    def perform_create(self, serializer):
        serializer.save()

class ContractListAllView(generics.ListAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    
    def get(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ContractListView(generics.ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ContractFilter
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    
    def get(self,request,*args,**kwargs):
        if not request.query_params:
            return Response({"error":"No query parameters provided"},status=status.HTTP_400_BAD_REQUEST)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
class ContractSummaryView(generics.ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ContractFilter
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset,many=True)
        contract_id_list = queryset.values_list('contract_id',flat=True)
        total_number_of_contracts = len(serializer.data)
        total_contracts_amount = sum([float(item['contract_amount']) for item in serializer.data]) or 0
        total_amount_to_receive = sum([float(item['parcel_amount']) for item in Parcel.objects.filter(contract_id__in=contract_id_list).values()]) or 0
        average_contract_rate = sum([float(item['contract_rate']) for item in serializer.data])/total_number_of_contracts if total_number_of_contracts > 0 else 0
        # for item in Parcel.objects.filter(contract_id__in=contract_id_list).all():
        #     print(item.parcel_number,item.parcel_due_date,item.parcel_amount)
        summary = {
            # 'total_contracts_amount': f"R$ {'%.2f'%(total_contracts_amount)}",
            # 'total_amount_to_receive': f"R$ {'%.2f'%(total_amount_to_receive)}",
            'total_contracts_amount': total_contracts_amount,
            'total_amount_to_receive': total_amount_to_receive,
            'total_number_of_contracts': total_number_of_contracts,
            'average_contract_rate': float('%.2f'%(average_contract_rate)),
        }
        return Response(summary,status=status.HTTP_200_OK)
