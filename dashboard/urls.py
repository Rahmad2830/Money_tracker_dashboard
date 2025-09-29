from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path("login/", views.sign_in, name="sign_in"),
  path("logout/", views.sign_out, name="sign_out"),
  path("kategori/", views.kategori, name="kategori"),
  path("transaksi/", views.transaksi, name="transaksi"),
  path("hapus/<str:model_name>/<int:id>", views.hapus_data, name="hapus_data"),
  path("kategori/edit_kategori/<int:pk>", views.edit_kategori, name="edit_kategori"),
  path("kategori/edit_transaksi/<int:pk>", views.edit_transaksi, name="edit_transaksi"),
  path("laporan/", views.laporan, name="laporan"),
  path("laporan/list_transaksi/<int:tahun>", views.transaksi_tahunan, name="transaksi_tahunan"),
  path("laporan/transaksi_bulanan/<int:tahun>/<int:bulan>", views.transaksi_bulanan, name="transaksi_bulanan"),
  path("export_tahunan/<int:tahun>", views.export_csv, name="export_tahunan"),
  path("export_tahunan/<int:tahun>/<int:bulan>", views.export_csv, name="export_bulanan"),
]