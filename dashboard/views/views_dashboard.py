from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from dashboard.forms import *
from django.apps import apps
from dashboard.models import Kategori, Transaksi

# Create your views here.
@login_required(login_url='sign_in')
def index(request):
  """Management saldo"""
  total_in = Transaksi.objects.filter(jenis="IN").aggregate(total=Sum("jumlah"))["total"] or 0
  total_out = Transaksi.objects.filter(jenis="OUT").aggregate(total=Sum("jumlah"))["total"] or 0
  saldo = total_in - total_out

  """top teratas transaksi"""
  bulan_ini = timezone.now().month
  tahun_ini = timezone.now().year
  top_pemasukan = Transaksi.objects.filter(created_at__month=bulan_ini, created_at__year=tahun_ini, jenis="IN").order_by("-jumlah")[:5]
  top_pengeluaran = Transaksi.objects.filter(created_at__month=bulan_ini, created_at__year=tahun_ini, jenis="OUT").order_by("-jumlah")[:5]

  """kirim ke frontend"""
  context = {
    "pemasukan": total_in,
    "pengeluaran": total_out,
    "saldo": saldo,
    "top_pemasukan": top_pemasukan,
    "top_pengeluaran": top_pengeluaran
  }
  return render(request, "dashboard/index.html", context)
  
@login_required(login_url="sign_in")
def kategori(request):
  query = request.GET.get("q", "")
  data = Kategori.objects.all().order_by("-created_at")
  if query:
    data = data.filter(
      Q(kategori__icontains=query)|
      Q(created_at__day__icontains=query)|
      Q(created_at__month__icontains=query)|
      Q(created_at__year__icontains=query)
    )
  paginator = Paginator(data, 20)
  page_number = request.GET.get("page")
  data_kategori = paginator.get_page(page_number)
  if request.method == "POST":
    form = KategoriForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect("kategori")
  else:
    form = KategoriForm()
  return render(request, "dashboard/kategori.html", {'form':form, 'data':data_kategori, 'query': query})
  
@login_required(login_url="sign_in")
def edit_kategori(request, pk):
  obj = get_object_or_404(Kategori, pk=pk)
  if request.method == "POST":
    form = EditKategoriForm(request.POST, instance=obj)
    if form.is_valid():
      form.save()
      return redirect("kategori")
  else:
    form = EditKategoriForm(instance=obj)
  return render(request, "dashboard/edit_kategori.html", {'form': form, 'data': obj})

@login_required(login_url="sign_in")
def transaksi(request):
  query = request.GET.get("q", "")
  data = Transaksi.objects.all().order_by("-created_at")
  if query:
    data = data.filter(
      Q(kategori_transaksi__kategori__icontains=query)|
      Q(jenis__icontains=query)|
      Q(created_at__day__icontains=query)|
      Q(created_at__month__icontains=query)|
      Q(created_at__year__icontains=query)
    )
  paginator = Paginator(data, 50)
  page_number = request.GET.get("page")
  data_transaksi = paginator.get_page(page_number)
  if request.method == "POST":
    form = TransaksiForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect("transaksi")
  else:
    form = TransaksiForm()
  return render(request, "dashboard/transaksi.html", {'form':form, 'data':data_transaksi, 'query': query})

@login_required(login_url="sign_in")
def edit_transaksi(request, pk):
  obj = get_object_or_404(Transaksi, pk=pk)
  if request.method == "POST":
    form = EditTransaksiForm(request.POST,instance=obj)
    if form.is_valid():
      form.save()
      return redirect("transaksi")
  else:
    form = EditTransaksiForm(instance=obj)
  return render(request, "dashboard/edit_transaksi.html", {'form': form, 'data': obj})
  
REDIRECT_AFTER_DELETE = {
  'Kategori': 'kategori',
  'Transaksi': 'transaksi'
}

@login_required(login_url="sign_in")
def hapus_data(request, model_name, id):
  model = apps.get_model('dashboard', model_name)
  obj = get_object_or_404(model, id=id)
  obj.delete()
  redirect_url = REDIRECT_AFTER_DELETE.get(model_name, '/')
  return redirect(redirect_url)

@login_required(login_url="sign_in")
def laporan(request):
  now = timezone.now()
  tahun_list = range(2020, now.year+1)
  bulan_list = range(1, 13)
  try:
    tahun = int(request.GET.get("tahun", now.year))
    bulan = int(request.GET.get("bulan", now.month))
  except ValueError:
    tahun = now.year
    bulan = now.month
  
  """Grafik Per Tahun"""
  data_grafik_tahunan = Transaksi.objects.filter(created_at__year=tahun).values("created_at__month", "jenis").annotate(total=Sum("jumlah"))
  
  pemasukan = [0] * 12
  pengeluaran = [0] * 12
  
  for row in data_grafik_tahunan:
    bln = row["created_at__month"] - 1
    if row["jenis"] == "IN":
      pemasukan[bln] = row["total"]
    elif row["jenis"] == "OUT":
      pengeluaran[bln] = row["total"]
  
  """Total Tahunan"""
  total_pemasukan_tahunan = Transaksi.objects.filter(created_at__year=tahun, jenis="IN").aggregate(total=Sum("jumlah"))["total"] or 0
  total_pengeluaran_tahunan = Transaksi.objects.filter(created_at__year=tahun, jenis="OUT").aggregate(total=Sum("jumlah"))["total"] or 0
  total_saldo_tahunan = total_pemasukan_tahunan - total_pengeluaran_tahunan
  
  """Rincian per Kategori"""
  total_by_kategori = Transaksi.objects.filter(created_at__year=tahun).values("kategori_transaksi__kategori").annotate(total=Sum("jumlah")).order_by("-total")
  
  """Perbandingan Selisih Tahunan/yoy"""
  data = {}
  tahun_sebelumnya = tahun - 1
  for thn in [tahun, tahun_sebelumnya]:
    income = Transaksi.objects.filter(created_at__year=thn, jenis="IN").aggregate(total=Sum("jumlah"))["total"] or 0
    expend = Transaksi.objects.filter(created_at__year=thn, jenis="OUT").aggregate(total=Sum("jumlah"))["total"] or 0
    total_saldo = income - expend
    data[thn] = {
      "pemasukan": income,
      "pengeluaran": expend,
      "saldo": total_saldo
    }
    
  yoy = {
    "pemasukan": data[tahun]["pemasukan"] - data[tahun_sebelumnya]["pemasukan"],
    "pengeluaran": data[tahun]["pengeluaran"] - data[tahun_sebelumnya]["pengeluaran"],
    "saldo": data[tahun]["saldo"] - data[tahun_sebelumnya]["saldo"]
  }
  
  """Laporan per bulan"""
  transaksi_bulanan_by_kategori = Transaksi.objects.filter(created_at__year=tahun, created_at__month=bulan).values("kategori_transaksi__kategori").annotate(total=Sum("jumlah"))
  
  labels = [item["kategori_transaksi__kategori"] for item in transaksi_bulanan_by_kategori]
  data_bulanan = [item["total"] for item in transaksi_bulanan_by_kategori]
  
  pemasukan_bulanan = Transaksi.objects.filter(created_at__year=tahun, created_at__month=bulan, jenis="IN").aggregate(total=Sum("jumlah"))["total"] or 0
  pengeluaran_bulanan = Transaksi.objects.filter(created_at__year=tahun, created_at__month=bulan, jenis="OUT").aggregate(total=Sum("jumlah"))["total"] or 0
  total_saldo_bulanan = pemasukan_bulanan - pengeluaran_bulanan
  
  """kirim ke frontend"""
  context = {
    "tahun_list": tahun_list,
    "bulan_list": bulan_list,
    "tahun_sekarang": tahun,
    "bulan_sekarang": bulan,
    "total_pemasukan_tahunan": total_pemasukan_tahunan,
    "total_pengeluaran_tahunan": total_pengeluaran_tahunan,
    "total_saldo_tahunan": total_saldo_tahunan,
    "perbandingan_tahunan": data,
    "yoy": yoy,
    "labels":labels,
    "data_bulanan_per_kategori":data_bulanan,
    "pemasukan_bulanan": pemasukan_bulanan,
    "pengeluaran_bulanan": pengeluaran_bulanan,
    "total_saldo_bulanan": total_saldo_bulanan,
    "total_by_kategori": total_by_kategori,
    "pemasukan": pemasukan,
    "pengeluaran": pengeluaran
  }
  
  return render(request, "dashboard/laporan.html", context)

@login_required(login_url="sign_in")
def transaksi_tahunan(request, tahun):
  transaksi_list = Transaksi.objects.filter(created_at__year=tahun).order_by("-created_at")
  paginator = Paginator(transaksi_list, 50)
  page_number = request.GET.get("page")
  transaksi_page = paginator.get_page(page_number)
  
  return render(request, "dashboard/list_transaksi.html", {'transaksi': transaksi_page, 'tahun': tahun})
  
@login_required(login_url="sign_in")
def transaksi_bulanan(request, tahun, bulan):
  transaksi_list = Transaksi.objects.filter(created_at__year=tahun, created_at__month=bulan).order_by("created_at")
  paginator = Paginator(transaksi_list, 50)
  page_number = request.GET.get("page")
  transaksi_page = paginator.get_page(page_number)
  
  return render(request, "dashboard/transaksi_bulanan.html", {'tahun': tahun, 'bulan': bulan, 'transaksi': transaksi_page})
  
@login_required(login_url="sign_in")
def settings(request):
  return render(request, "dashboard/settings.html")

@login_required(login_url="sign_in")
def export_csv(request, tahun=None, bulan=None):
  qs = Transaksi.objects.all()
  
  if tahun:
    qs.filter(created_at__year=tahun)
    filename = f"transaksi_{tahun}.csv"
  elif tahun and bulan:
    qs.filter(created_at__year=tahun, created_at__month=bulan)
    filename = f"transaksi_{bulan}_{tahun}.csv"
  
  response = HttpResponse(content_type="text/csv")
  response["Content-Disposition"] = f'attachment; filename="{filename}"'
  
  writer = csv.writer(response)
  writer.writerow(["Tanggal", "Jenis", "Kategori", "Jumlah"])
  
  for t in qs.iterator():
    writer.writerow([
      t.created_at.strftime("%Y-%m-%d %H:%M"),
      t.get_jenis_display(),
      t.kategori_transaksi,
      f"Rp {t.jumlah:,}".replace(",", ".")
    ])
    
  return response
  
