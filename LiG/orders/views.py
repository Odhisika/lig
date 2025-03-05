from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.timezone import now
from decimal import Decimal
import json

from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product


@login_required
def payments(request):
    try:
        body = json.loads(request.body)
        order = get_object_or_404(Order, user=request.user, is_ordered=False, order_number=body.get('orderID'))

        # Store transaction details inside Payment model
        payment = Payment.objects.create(
            user=request.user,
            payment_id=body.get('transID'),
            payment_method=body.get('payment_method'),
            amount_paid=order.order_total,
            status=body.get('status'),
        )

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            order_product = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True
            )

            # Add product variations
            order_product.variations.set(item.variations.all())
            order_product.save()

            # Reduce stock of sold products
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart
        cart_items.delete()

        # Send order confirmation email
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        try:
            send_email = EmailMessage(mail_subject, message, to=[request.user.email])
            send_email.send()
        except Exception as e:
            print(f"Email sending failed: {e}")

        # Send response back to frontend
        return JsonResponse({
            'order_number': order.order_number,
            'transID': payment.payment_id,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    if not cart_items.exists():
        return redirect('store')

    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = Decimal(total * 0.02).quantize(Decimal('0.01'))  # 2% tax
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = current_user
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR', '')
            data.save()

            # Generate order number
            order_number = now().strftime("%Y%m%d") + str(data.id)
            data.order_number = order_number
            data.save()

            order = get_object_or_404(Order, user=current_user, is_ordered=False, order_number=order_number)

            return render(request, 'orders/payments.html', {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            })

    return redirect('checkout')


@login_required
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
    ordered_products = OrderProduct.objects.filter(order=order)
    subtotal = sum(item.product_price * item.quantity for item in ordered_products)

    payment = get_object_or_404(Payment, payment_id=transID)

    return render(request, 'orders/order_complete.html', {
        'order': order,
        'ordered_products': ordered_products,
        'order_number': order.order_number,
        'transID': payment.payment_id,
        'payment': payment,
        'subtotal': subtotal,
    })
