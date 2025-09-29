from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Kategori, Transaksi

class CustomLoginForm(AuthenticationForm):
  username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
  password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
  
class KategoriForm(forms.ModelForm):
  kategori = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
  class Meta:
    model = Kategori
    fields = ["kategori"]
    
class TransaksiForm(forms.ModelForm):
  class Meta:
    model = Transaksi
    fields = ["kategori_transaksi", "jenis", "jumlah"]
    widgets = {
      "kategori_transaksi": forms.Select(attrs={"class": "form-select"}),
      "jenis": forms.Select(attrs={"class": "form-select"}),
      "jumlah": forms.NumberInput(attrs={"class": "form-control"}),
    }
    
class EditKategoriForm(forms.ModelForm):
  class Meta:
    model = Kategori
    fields = ["kategori"]
    widgets = {
      "kategori": forms.TextInput(attrs={"class": "form-control"})
    }
    
class EditTransaksiForm(forms.ModelForm):
  class Meta:
    model = Transaksi
    fields = ["kategori_transaksi", "jenis", "jumlah"]
    widgets = {
      "kategori_transaksi": forms.Select(attrs={"class": "form-select"}),
      "jenis": forms.Select(attrs={"class": "form-select"}),
      "jumlah": forms.NumberInput(attrs={"class": "form-control"})
    }