from django.db import models

class MesureRefroidisseur(models.Model):
    date_heure = models.DateTimeField()
    debit_farine = models.FloatField()
    commentaires = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Mesure {self.id} - {self.date_heure.strftime('%d/%m/%Y %H:%M')}"


class VentilateurMesure(models.Model):
    mesure = models.ForeignKey(MesureRefroidisseur, on_delete=models.CASCADE, related_name='ventilateurs')
    nom = models.CharField(max_length=50)
    debit = models.FloatField()

    def __str__(self):
        return f"{self.nom}: {self.debit} Nm³/h (Mesure {self.mesure.id})"


class ResultatCalcul(models.Model):
    mesure = models.ForeignKey(MesureRefroidisseur, on_delete=models.CASCADE, related_name='resultats')
    grate = models.CharField(max_length=100)
    chambre = models.CharField(max_length=20)
    fan = models.CharField(max_length=100)
    flow = models.FloatField()
    flow_specifique = models.FloatField()
    area = models.FloatField()
    sp_air_load = models.FloatField()
    sp_air_load_kg = models.FloatField()

    def __str__(self):
        return f"{self.grate} (Mesure {self.mesure.id})"
# models.py

class MesureImage(models.Model):
    mesure = models.ForeignKey('MesureRefroidisseur', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='mesure_images/')