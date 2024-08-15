from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.contrib.auth import login ,logout,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trip, Expense,Category

#password rest 
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

#pdf covertion 
from xhtml2pdf import pisa
from io import BytesIO

# mail setup 
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

def home(request):
    return render(request,'home.html')

def admin_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_staff:
                login(request,user)
                return redirect('home')
            else:
                messages.error(request,"sorry you'r not admin/staff")
                return redirect('login')
        else:
           messages.error(request,'please check password | username')
           return redirect('Admin')
    return render(request,'admin.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            user=User.objects.get(username=username)
            if user.check_password(password):
                if user.is_active:
                    user = authenticate(username=username,password=password)
                    if user is not None:
                        login(request,user)
                        messages.success(request,'login successfull')
                        return redirect('home')
                    else:
                       messages.error(request,'please check the Password Properly')
                       return redirect('login')
                else:
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    return render(request,'Acc-act/Reactivate_acc.html',{'username':user,'uid':uid})
            else:
                messages.error(request,"please check the Password Properly")  
                return redirect('login') 
        else:
            messages.error(request,"username doesn't exist")
            return redirect('login')
    return render(request,'user.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        First_Name = request.POST['name']
        Email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirmation_password = request.POST['cnfm_password']
        select_user = request.POST['select_user']
        if select_user == 'admin':
            select_user = True
        else:
            select_user = False
        if password == confirmation_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists, please choose a different one.')
                return redirect('register')
            else:
                if User.objects.filter(email=Email).exists():
                    messages.error(request, 'Email already exists, please choose a different one.')
                    return redirect('register')
                else:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=Email,
                        first_name=First_Name,
                        is_staff=select_user,
                        is_active=False  
                    )
                    send_activation_email(user,request)
                    return render(request,'Acc-act/mail_send.html',{'email':Email})
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
    return render(request, 'register.html')

def trip_list(request):
    trips = Trip.objects.all()
    return render(request, 'trip_list.html', {'trips': trips})


def add_trip(request):
    if request.method=="POST":
        name = request.POST['trip']
        start_date = request.POST['start_date']
        end_date =request.POST['end_date']
        data=Trip.objects.create(user=request.user,name=name,start_date=start_date,end_date=end_date)
        messages.success(request,'Trip added successfully')
        return redirect('add_trip')
    return render(request, 'add_trip.html')


def add_expense(request):
    category=Category.objects.all()
    trip=Trip.objects.filter(user=request.user,status='pending')
    if request.method=="POST":
        trip_id=request.POST['Trip']
        category_id=request.POST['category']
        Date=request.POST['date']
        price=request.POST['price']
        Description=request.POST['description']
        trip=Trip.objects.get(id=trip_id)
        category=Category.objects.get(id=category_id)
        data=Expense.objects.create(trip=trip,category=category,date=Date,amount=price,description=Description)
        data.save()
        messages.success(request,'Expense added successfully')
        return redirect('add_expense')
    return render(request, 'add_expense.html', {'categories': category,'trips':trip})


def add_category(request):
    categories=Category.objects.all()
    if request.method=="POST":
        category=request.POST['category']
        data=Category.objects.create(name=category)
        messages.success(request,'Saved expense Sucessfully')
        return redirect('add_category')
    return render(request,'add_category.html',{'categories':categories})


def trip_list(request):
    trips=Trip.objects.filter(user=request.user)
    return render(request,'trip_list.html',{'trips':trips})


def expense_list(request,pk):
    trip=Trip.objects.get(id=pk,user=request.user)
    expenses=Expense.objects.filter(trip=trip)
    amount=sum(item.amount for item in expenses)
    return render(request,'expenselist.html',{'expenses':expenses,'trip':trip,'amount':amount})    


def finsih_trip(request,pk):
    trip=Trip.objects.get(id=pk,user=request.user)
    if trip.status == 'pending':
        trip.status = 'Done'
        trip.save()
    return redirect('trips_list')    

#acc Reactivate
def reactivate_acc(request,uidb64):
    uid = force_text(urlsafe_base64_decode(uidb64))
    user=User.objects.get(pk=uid)
    send_activation_email(user, request)
    
    return render(request,'Acc-act/reactivate_message.html')

# mail setup 
def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    domain = current_site.domain
    activation_link = f"http://{domain}/activate/{uid}/{token}/"
    
    subject = 'Activate Your Account'
    html_message = render_to_string('Acc-act/activation_email.html', {
        'user': user,
        'activation_link': activation_link,
    })
    email = EmailMultiAlternatives(
        subject,
        html_message,  
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.attach_alternative(html_message, "text/html") 
    email.send()

    
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None   
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')  
    else:
        return render(request, 'Acc-act/activation_invalid.html')
    
#pdf Download Setup

def render_to_pdf(template_src, context_dict={}):
    template = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(template, dest=result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def invoice_pdf_view(request, trip_id):
    trip=Trip.objects.get(id=trip_id)
    data = Expense.objects.filter(trip=trip)
    amount=sum(item.amount for item in data)
    context = {
        'invoice': data,
        'trip':trip,
        'amount':amount,
        }
    return render_to_pdf('invoice_template.html', context)