from django.db import models

class Kategori(models.Model):
  kategori = models.CharField(max_length=200)
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.kategori
    
class Transaksi(models.Model):
  JENIS_CHOICE = [
    ("IN", "pemasukan"),
    ("OUT", "pengeluaran"),
  ]
  kategori_transaksi = models.ForeignKey("Kategori", on_delete=models.CASCADE)
  jenis = models.CharField(choices=JENIS_CHOICE)
  jumlah = models.IntegerField()
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"{self.kategori_transaksi.kategori} ({self.get_jenis_display()}) - {self.jumlah}"