from django.shortcuts import redirect, render
from accounts.forms import RegistrationForm
from accounts.models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

# Create your views here.
def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password) # type: ignore
            user.phone_number = phone_number
            user.is_active = True
            user.save()

            messages.success(request, 'Se registro el usuario existosamente')
            return redirect('login')
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)
            if user is not None:
                 try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))
                        cart_item = CartItem.objects.filter(user=user)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation= item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id) # type: ignore

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index] # type: ignore
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user # type: ignore
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user # type: ignore
                                    item.save()
                            
                        
                 except:
                    pass
                 auth.login(request, user)
                 
                 messages.success(request, 'Has iniciado sesion exitosamente')
                 url = requests.META.get('HTTP_REFERER') # type: ignore
                 try:
                     query = requests.utils.urlparse(url).query # type: ignore
                     params = dict(x.split('=') for x in query.split('&'))
                     if 'next' in params:
                         nextPage = params['next']
                         return redirect(nextPage)
                 except:
                     return redirect('dashboard')
                 
            else:
                 messages.error(request, 'Las credenciales son incorrectas')
                 print(user)
                 return redirect('login')
                
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Ha salido de sesion")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
         user = None
    if user is not None and default_token_generator.check_token(user, token):
         user.is_active = True
         user.save()
         messages.success(request, 'Felicidades, tu cuenta esta activa!')
         return redirect('login')
    else:
         messages.error(request, 'La activacion es invalida')
         return redirect('register')
    
@login_required(login_url='login')
def dashboard(request):
     return render(request, 'accounts/dashboard.html')