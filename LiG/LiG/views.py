from django.shortcuts import render
from store.models import Product,Category,ReviewRating

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)


def allproducts(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, 'hardware/allproducts.html', context)





### Hardware ###

def desktops(request):
    try:
        desktops_category = Category.objects.get(category_name="Desktop")
        products = Product.objects.filter(category=desktops_category, is_available=True)
    except Category.DoesNotExist:
        products = []

    context = {
        'products': products
    }
    return render(request, 'hardware/desktop.html',context)  


def laptops(request):
    try:
        laptops_category = Category.objects.get(category_name="Laptops")
        products = Product.objects.filter(category=laptops_category, is_available=True)
    except Category.DoesNotExist:
        products = []
    
    context = {
        'products': products
    }
    return render(request, 'hardware/laptop.html',context)  

def peripherals(request):
    try:
        laptops_category = Category.objects.get(category_name="Peripherals")
        products = Product.objects.filter(category=laptops_category, is_available=True)
    except Category.DoesNotExist:
        products = []
    
    context = {
        'products': products
    }
    return render(request, 'hardware/peripherals.html', context) 

### Software ###
def operatingSystems(request):
    return render(request, 'software/operatingSystems.html')

def applications(request):
    return render(request, 'software/applications.html')

def developmentTools(request):
    return render(request, 'software/developmentTools.html')

### IT solutions ###

def cctv(request):
    return render(request, 'itSolution/CCTVInstallation.html')

def hardwareRepairs(request):
    return render(request, 'itSolution/hardwareRepairs.html')

def networkingSolutions(request):
    return render(request, 'itSolution/networkingSolutions.html')

## Research Hub##

def caseStudies(request):
    return render(request, 'research/caseStudies.html')

def whitePapers(request):
    return render(request, 'research/whitePapers.html')

def techTrends(request):
    return render(request, 'research/techTrends.html')
