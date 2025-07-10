from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Prefetch, Q

from hotel.models import Booking, Notification, Bookmark, Hotel, Review, Room, RoomType
from userauths.models import Profile, User
from userauths.forms import ProfileUpdateForm, UserUpdateForm

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(
        user=request.user, 
        payment_status="paid"
    ).select_related(
        'hotel', 
        'user', 
        'room_type'
    )
    
    total_spent = Booking.objects.filter(
        user=request.user, 
        payment_status="paid"
    ).aggregate(amount=Sum('total'))

    print("bookings ========", total_spent)
    context = {
        "bookings": bookings,
        "total_spent": total_spent,
    }
    return render(request, "user_dashboard/dashboard.html", context)

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related(
            'hotel', 
            'user', 
            'room_type'
        ),
        booking_id=booking_id
    )

    context = {
        "booking": booking,
    }
    return render(request, "user_dashboard/booking_detail.html", context)

@login_required
def bookings(request):
    bookings = Booking.objects.filter(
        user=request.user, 
        payment_status="paid"
    ).select_related(
        'hotel', 
        'user', 
        'room_type'
    )

    context = {
        "bookings": bookings,
    }
    return render(request, "user_dashboard/bookings.html", context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user, 
        seen=False
    ).select_related(
        'user', 
        'booking'
    )

    context = {
        "notifications": notifications,
    }
    return render(request, "user_dashboard/notifications.html", context)

def notification_filter(request):
    query = request.GET['query']
    
    notifications_query = Notification.objects.filter(
        user=request.user
    ).select_related(
        'user', 
        'booking'
    )
    
    if query == "read":
        notifications = notifications_query.filter(seen=True)
    elif query == "unread":
        notifications = notifications_query.filter(seen=False)
    else:
        notifications = notifications_query
    
    context = render_to_string("user_dashboard/async/notifications.html", {"notifications": notifications})
    return JsonResponse({"data": context})

def notification_mark_as_seen(request):
    id = request.GET['id']
    notification = get_object_or_404(Notification, id=id)
    notification.seen = True
    notification.save(update_fields=['seen'])
    
    return JsonResponse({"data": _("Marked As Seen")})

@login_required
def wallet(request):
    bookings = Booking.objects.filter(
        user=request.user, 
        payment_status="paid"
    ).select_related(
        'hotel', 
        'user', 
        'room_type'
    )
    
    total_spent = Booking.objects.filter(
        user=request.user, 
        payment_status="paid"
    ).aggregate(amount=Sum('total'))

    context = {
        "bookings": bookings,
        "total_spent": total_spent,
    }
    return render(request, "user_dashboard/wallet.html", context)

@login_required
def bookmark(request):
    bookmark = Bookmark.objects.filter(
        user=request.user
    ).select_related(
        'user', 
        'hotel'
    )

    context = {
        "bookmark": bookmark,
    }
    return render(request, "user_dashboard/bookmark.html", context)

@login_required
def delete_bookmark(request, bid):
    bookmark = get_object_or_404(Bookmark, bid=bid, user=request.user)
    bookmark.delete()
    return redirect("dashboard:bookmark")

def add_to_bookmark(request):
    id = request.GET['id']
    hotel = get_object_or_404(Hotel, id=id)
    
    if request.user.is_authenticated:
        try:
            bookmark = Bookmark.objects.get(user=request.user, hotel=hotel)
            bookmark.delete()
            return JsonResponse({"data": _("Bookmark Deleted"), "icon": "success"})
        except Bookmark.DoesNotExist:
            Bookmark.objects.create(user=request.user, hotel=hotel)
            return JsonResponse({"data": _("Hotel Bookmarked"), "icon": "success"})
    else:
        return JsonResponse({"data": _("Login To Bookmark Hotel"), "icon": "warning"})

@login_required
def profile(request):
    profile = get_object_or_404(Profile.objects.select_related('user'), user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, _("Profile Updated Successfully"))
            return redirect("dashboard:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        "profile": profile,
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "user_dashboard/profile.html", context)

@login_required
def password_changed(request):
    return render(request, "user_dashboard/password_changed.html")

@login_required
def add_review(request):
    id = request.GET['id']
    rating = request.GET['rating']
    review_text = request.GET['review']
    
    hotel = get_object_or_404(Hotel, id=id)

    review_exists = Review.objects.filter(user=request.user, hotel=hotel).exists()
    
    if review_exists:
        return JsonResponse({"data": _("Review Already Exists"), "icon": "warning"})
    else:
        Review.objects.create(
            user=request.user,
            rating=rating,
            hotel=hotel,
            review=review_text
        )
        return JsonResponse({"data": _("Review Submitted, Thank You"), "icon": "success"})
    
