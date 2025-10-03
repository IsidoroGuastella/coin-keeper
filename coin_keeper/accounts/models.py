from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.username

class Stato(models.Model):
    nome = models.CharField(max_length=100)
    iso2 = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.nome

class Moneta(models.Model):
    stato = models.ForeignKey(Stato, on_delete=models.CASCADE, related_name="monete")
    valore_nominale = models.CharField(max_length=50)  # es: "2 Euro", "50 Cent"
    anno_conio = models.IntegerField()

    def __str__(self):
        return f"{self.valore_nominale} - {self.anno_conio} ({self.stato.nome})"

class Luogo(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Esemplare(models.Model):
    utente = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="esemplari")
    moneta = models.ForeignKey(Moneta, on_delete=models.CASCADE, related_name="esemplari")
    luogo = models.ForeignKey(Luogo, on_delete=models.SET_NULL, null=True, blank=True, related_name="esemplari")
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.moneta} di {self.utente.username}"
