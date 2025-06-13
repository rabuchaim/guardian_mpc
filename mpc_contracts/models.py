from django.db import models

class Contract(models.Model):
    contract_id = models.BigAutoField(primary_key=True)
    contract_date = models.DateField()
    contract_amount = models.DecimalField(max_digits=11,decimal_places=2)
    contract_rate = models.FloatField(max_length=3)
    customer_cpf = models.CharField(max_length=14) # 14 para aceitar com pontos e traços (será filtrado)
    customer_birth_date = models.DateField()
    # customer_address = models.CharField(max_length=255)
    customer_city = models.CharField(max_length=100)
    customer_state = models.CharField(max_length=2)
    customer_country = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    def __str__(self):
        return f"Contract {self.contract_id} - CPF:{self.customer_cpf} - Amount: R$ {self.contract_amount}"

class Parcel(models.Model):
    contract_id = models.ForeignKey(Contract,on_delete=models.CASCADE,related_name='parcel')
    parcel_number = models.IntegerField()
    parcel_amount = models.DecimalField(max_digits=11,decimal_places=2)
    parcel_due_date = models.DateField()
    def __str__(self):
        return f"Contract {self.contract_id} - Parcel:{self.parcel_number} - Amount: R$ {self.parcel_amount}"