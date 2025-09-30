from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from dashboard.forms import CustomLoginForm
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', block=True)
def sign_in(request):
  if request.user.is_authenticated:
    return redirect("index")
    
  if request.method == "POST":
    form = CustomLoginForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      return redirect("index")
  else:
    form = CustomLoginForm()
  return render(request, "dashboard/auth/login.html", {'form': form})

def sign_out(request):
  logout(request)
  return redirect("sign_in")
