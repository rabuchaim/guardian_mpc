from rest_framework import serializers
from .models import Contract, Parcel
from .validators import validate_cpf, validate_uf_code
from datetime import datetime as dt

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = '__all__'
        read_only_fields = ['contract_id','parcel_number'] # Auto-incremento

class ContractSerializer(serializers.ModelSerializer):
    parcels = ParcelSerializer(many=True,required=False)
    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ['contract_id']  # Auto-incremento

    ##──── VALIDAÇÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    def validate_customer_cpf(self,value): # retorna o CPF filtrado (somente dígitos) e validado
        cpf = validate_cpf(value)
        return cpf
    def validate_customer_state(self,value): # retorna a sigla do estado normalizada (upper) e validada
        UF = validate_uf_code(value)
        return UF
    ##─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    def create(self, validated_data):
        data_parcels = validated_data.pop('parcels',[])
        
        if 'contract_date' not in validated_data:
            raise serializers.ValidationError("Contract date is required.")
        try:
            date_obj = dt.strptime(str(validated_data['contract_date']),"%Y-%m-%d").date()
        except ValueError:
            raise serializers.ValidationError("Invalid contract date format. Expected format: YYYY-MM-DD.")

        if validated_data['contract_amount'] <= 0:
            raise serializers.ValidationError("Contract amount must be greater than zero.")
        if validated_data['contract_rate'] < 0:
            raise serializers.ValidationError("Contract rate must be zero or positive.")

        if not data_parcels:
            raise serializers.ValidationError("At least one parcel must be provided.")
        if any(parcel['parcel_amount'] <= 0 for parcel in data_parcels):
            raise serializers.ValidationError("All parcel amounts must be greater than zero.")
        if any(parcel['parcel_due_date'] <= validated_data['contract_date'] for parcel in data_parcels):
            raise serializers.ValidationError("All parcel due dates must be after the contract date.")
        sum_parcels = float(sum(parcel['parcel_amount'] for parcel in data_parcels))
        to_receive = float(validated_data['contract_amount']) * validated_data['contract_rate']
        # print(sum_parcels,to_receive)
        if sum_parcels < to_receive:
            raise serializers.ValidationError(f"The total of parcel amounts must be greater than or equal to the contract amount multiplied by contract rate. In this case, greater than or equal to {to_receive}")
        data_contract = Contract.objects.create(**validated_data)
        for i, parcel_data in enumerate(data_parcels):
            Parcel.objects.create(contract_id=data_contract,parcel_number=i+1,**parcel_data)
        return data_contract
