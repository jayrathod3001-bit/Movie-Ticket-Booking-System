from decimal import Decimal
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.http import HttpResponse
from io import BytesIO
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from JK.models import (
    add_movie,
    coming_movie,
    RegisterUser,
    Theatre,
    Booking,
    CancelBooking
)

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.conf import settings
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False
import json
from django.db import transaction
from django.contrib import messages
# ===================== HOME PAGE =====================

def renderpage(request):
    data1 = add_movie.objects.all()
    data2 = coming_movie.objects.all()

    genre_list = list(add_movie.objects.values_list('Genre', flat=True).distinct()) + \
                 list(coming_movie.objects.values_list('C_Genre', flat=True).distinct())
    genre_list = sorted(set(filter(None, genre_list)))

    language_list = list(add_movie.objects.values_list('Language', flat=True).distinct()) + \
                    list(coming_movie.objects.values_list('C_Language', flat=True).distinct())

    hero_list = list(add_movie.objects.values_list('Hero', flat=True).distinct()) + \
                list(coming_movie.objects.values_list('C_Hero', flat=True).distinct())

    heroine_list = list(add_movie.objects.values_list('Heroine', flat=True).distinct()) + \
                   list(coming_movie.objects.values_list('C_Heroine', flat=True).distinct())

    certificate_list = list(add_movie.objects.values_list('Certificate', flat=True).distinct()) + \
                       list(coming_movie.objects.values_list('C_Certificate', flat=True).distinct())

    rating_list = list(add_movie.objects.values_list('Rating', flat=True).distinct()) + \
                  list(coming_movie.objects.values_list('C_Rating', flat=True).distinct())

    status_list = ["Now Showing", "Coming Soon"]

    user = None
    if request.session.get("username"):
        try:
            user = RegisterUser.objects.filter(username=request.session.get("username")).first()
        except RegisterUser.DoesNotExist:
            user = None

    data = {
        "movie": data1,
        "coming": data2,
        "genre_list": genre_list,
        "hero_list": hero_list,
        "heroine_list": heroine_list,
        "language_list": language_list,
        "certificate_list": certificate_list,
        "rating_list": rating_list,
        "status_list": status_list,
        "user": user,
    }

    return render(request, "home.html", data)


# ===================== AUTH SYSTEM =====================

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()

            # ------------ SEND EMAIL ------------
            subject = "Registration Successful!"
            message = (
                f"Hello {user.username},\n\n"
                "Your account has been created successfully.\n"
                "Welcome to our Movie Ticket Booking System!\n\n"
                "Thank you!"
            )

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,       # sender Gmail
                [user.email],                   # recipient (user's email)
                fail_silently=False,
            )
            # -------------------------------------

            request.session["username"] = user.username
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password1")

        try:
            user = RegisterUser.objects.get(email=email, password1=password)
            request.session["username"] = user.username
            return redirect("home")
        except RegisterUser.DoesNotExist:
            error = "Invalid email or password"

    return render(request, "login.html", {"error": error})


def logout_view(request):
    request.session.flush()
    return redirect("home")


# ===================== PROFILE SYSTEM =====================

def view_profile(request):
    if 'username' not in request.session:
        return redirect('login')

    try:
        user = RegisterUser.objects.filter(username=request.session.get("username")).first()
    except RegisterUser.DoesNotExist:
        return redirect('login')

    context = {'user': user}
    return render(request, 'view_profile.html', context)


def update_profile(request):
    if 'username' not in request.session:
        return redirect('login')

    user = get_object_or_404(RegisterUser, username=request.session['username'])

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.gender = request.POST.get('gender')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')

        birth_date = request.POST.get('birth_date')
        if birth_date:
            user.birth_date = birth_date     # correct format
        else:
            user.birth_date = None           # error fix

        # Password update only if user enters
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1:
            if password1 == password2:
                user.password1 = password1
                user.password2 = password2
            else:
                messages.error(request, "Passwords do not match!")
                return render(request, 'update_profile.html', {'user': user})

        # Profile photo update
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')

        user.save()
        request.session['username'] = user.username
        messages.success(request, "Profile updated successfully!")
        return redirect('update_profile')

    return render(request, 'update_profile.html', {'user': user})

# ===================== MOVIE DETAILS =====================

def movie_detail(request, movie_id):
    movie = add_movie.objects.get(a_id=movie_id)
    return render(request, "movie_detail.html", {"movie": movie})


# ===================== BOOKING PAGES =====================
def timing(request):
    if "username" not in request.session:
        return redirect("/login/?next=/timing/")

    # movie_id query string se lo
    movie_id = request.GET.get("movie_id")

    # agar movie_id nahi mila to home bhej do
    if not movie_id:
        return redirect("home")

    # correct movie DB se nikaalo
    movie = get_object_or_404(add_movie, pk=movie_id)

    theatres = Theatre.objects.all()

    context = {
        "movie": movie,
        "theatres": theatres,
    }
    return render(request, "timing.html", context)


def seat(request):
    # seat selection page expects movie_id, theatre_id, show_date, show_time as GET params.
    if "username" not in request.session:
        return redirect("/login/?next=/seat/")

    movie_id = request.GET.get("movie_id")
    theatre_id = request.GET.get("theatre_id")
    show_date_str = request.GET.get("show_date")   # expected format: YYYY-MM-DD or whatever you passed
    show_time = request.GET.get("show_time")

    # If params not provided, redirect to timing or home — prevent blank seat page
    if not (movie_id and theatre_id and show_time and show_date_str):
        messages.error(request, "Please select movie, theatre, date and time first.")
        return redirect("timing")

    # fetch objects (404 if bad)
    movie = get_object_or_404(add_movie, pk=movie_id)
    theatre = get_object_or_404(Theatre, pk=theatre_id)

    # parse show_date (try to be flexible)
    from datetime import datetime
    show_date = None
    try:
        # try YYYY-MM-DD first
        show_date = datetime.strptime(show_date_str, "%Y-%m-%d").date()
    except Exception:
        try:
            # fallback: if your front-end uses "Mon Dec 08" format, you may already pass full date in confirm_booking
            current_year = datetime.now().year
            show_date = datetime.strptime(f"{show_date_str} {current_year}", "%a %b %d %Y").date()
        except Exception:
            # if cannot parse, leave as None (we'll still fetch by string)
            show_date = None

    # Query bookings that are already paid for the same movie/theatre/date/time
    if show_date:
        existing_bookings = Booking.objects.filter(
            movie=movie, theatre=theatre, show_date=show_date, show_time=show_time, is_paid=True
        )
    else:
        # If date parse failed, try matching by raw string (less safe) — keep backward compatibility
        existing_bookings = Booking.objects.filter(
            movie=movie, theatre=theatre, show_time=show_time, is_paid=True
        )

    # collect all booked seat numbers into a flat list of strings (trimmed)
    booked_seats = []
    for b in existing_bookings:
        if b.seats:
            seats_list = [s.strip() for s in b.seats.split(",") if s.strip()]
            booked_seats.extend(seats_list)

    # remove duplicates
    booked_seats = sorted(set(booked_seats), key=lambda x: int(x) if x.isdigit() else x)

    context = {
        "movie": movie,
        "theatre": theatre,
        "show_date": show_date_str,
        "show_time": show_time,
        "booked_seats": booked_seats,
        "booked_seats_json": json.dumps(booked_seats),  # pass as JSON for JS
    }
    return render(request, "seat.html", context)


# ---------- PAYMENT (DUMMY SCANNER) ----------
def payment(request):
    if "username" not in request.session:
        return redirect("/login/?next=/payment/")

    # data localStorage se aa rahi hai, yaha sirf template render
    return render(request, "payment.html")


# ----------  PAYMENT CONFIRM => BOOKING CREATE ----------
def confirm_booking(request):
    # local imports so you don't need to modify top-of-file imports
    import logging
    from django.db import transaction

    logger = logging.getLogger(__name__)

    if "username" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("payment")

    # ensure we have user object
    user = RegisterUser.objects.filter(username=request.session.get("username")).first()
    if not user:
        messages.error(request, "Please login again to complete booking.")
        return redirect("login")

    # Read POST safely
    movie_id_raw = request.POST.get("movie_id")
    theatre_id_raw = request.POST.get("theatre_id")
    show_time = request.POST.get("show_time")
    show_date_str = request.POST.get("show_date")
    seats = request.POST.get("seats")  # expected "1,2,3"
    total_price_raw = request.POST.get("total_price") or request.POST.get("total_price_input") or "0"

    # Basic validation: ensure important fields exist
    if not movie_id_raw or not theatre_id_raw or not show_time or not show_date_str or not seats:
        messages.error(request, "Booking data missing. Please reselect seats and try again.")
        return redirect("timing")

    # Try converting ids to int
    try:
        movie_id = int(movie_id_raw)
        theatre_id = int(theatre_id_raw)
    except Exception:
        messages.error(request, "Invalid booking data (movie/theatre). Please reselect seats.")
        return redirect("timing")

    # Parse total_price safely
    try:
        total_price = Decimal(total_price_raw)
    except Exception:
        total_price = Decimal("0")

    # parse show_date (try ISO YYYY-MM-DD first)
    show_date = None
    try:
        show_date = datetime.strptime(show_date_str, "%Y-%m-%d").date()
    except Exception:
        try:
            current_year = datetime.now().year
            show_date_full_str = f"{show_date_str} {current_year}"
            show_date = datetime.strptime(show_date_full_str, "%a %b %d %Y").date()
        except Exception:
            # leave show_date as None; downstream queries will ignore date
            show_date = None

    # ensure seats are valid integers
    try:
        seat_numbers = [int(s.strip()) for s in seats.split(",") if s.strip()]
    except Exception:
        messages.error(request, "Invalid seat selection. Please reselect seats.")
        return redirect(f"/seat/?movie_id={movie_id}&theatre_id={theatre_id}&show_date={show_date_str}&show_time={show_time}")

    total_seats = len(seat_numbers)

    # fetch objects
    try:
        movie = get_object_or_404(add_movie, pk=movie_id)
        theatre = get_object_or_404(Theatre, pk=theatre_id)
    except Exception:
        messages.error(request, "Selected movie or theatre not found. Please try again.")
        return redirect("home")

    # categorize seats
    seatTypesPrice = {'VIP': 500, 'PREMIUM': 350, 'REGULAR': 250}
    vip_seats = [s for s in seat_numbers if s <= 20]
    premium_seats = [s for s in seat_numbers if 21 <= s <= 60]
    regular_seats = [s for s in seat_numbers if s > 60]

    seat_type_str = []
    if vip_seats: seat_type_str.append(f"VIP (₹{seatTypesPrice['VIP']})")
    if premium_seats: seat_type_str.append(f"Premium (₹{seatTypesPrice['PREMIUM']})")
    if regular_seats: seat_type_str.append(f"Regular (₹{seatTypesPrice['REGULAR']})")
    seat_type_str = ", ".join(seat_type_str)

    # Server-side availability check (atomic)
    try:
        with transaction.atomic():
            if show_date:
                existing_qs = Booking.objects.select_for_update().filter(
                    movie=movie, theatre=theatre, show_date=show_date, show_time=show_time, is_paid=True
                )
            else:
                existing_qs = Booking.objects.select_for_update().filter(
                    movie=movie, theatre=theatre, show_time=show_time, is_paid=True
                )

            already_booked = set()
            for eb in existing_qs:
                if eb.seats:
                    already_booked.update([s.strip() for s in eb.seats.split(",") if s.strip()])

            requested_set = set([str(s) for s in seat_numbers])
            conflict = requested_set.intersection(already_booked)

            if conflict:
                conflict_list = ", ".join(sorted(conflict, key=lambda x: int(x) if x.isdigit() else x))
                messages.error(request, f"Sorry — these seats were just booked by someone else: {conflict_list}. Please choose different seats.")
                params = f"?movie_id={movie_id}&theatre_id={theatre_id}&show_date={show_date_str}&show_time={show_time}"
                return redirect("/seat/" + params)

            # create booking
            booking = Booking.objects.create(
                user=user,
                movie=movie,
                theatre=theatre,
                show_time=show_time,
                show_date=show_date,
                seats=seats,
                seat_type=seat_type_str,
                tickets=total_seats,
                total_price=total_price,
                is_paid=True,
            )
    except Exception as e:
        logger.exception("Error during booking: %s", e)
        messages.error(request, "Something went wrong while creating booking. Please try again.")
        return redirect(f"/seat/?movie_id={movie_id}&theatre_id={theatre_id}&show_date={show_date_str}&show_time={show_time}")

    # store session and send email (best-effort)
    request.session["seat_numbers"] = seats
    request.session["total_seats"] = total_seats

    try:
        subject = f"🎟 Your Ticket for {movie.Movie_Name}"
        to_email = user.email
        message_html = render_to_string('email/ticket_email.html', {
            'booking': booking,
            'seat_numbers': seat_numbers,
            'vip_seats': vip_seats,
            'premium_seats': premium_seats,
            'regular_seats': regular_seats,
            'seat_type_str': seat_type_str,
            'total_seats': total_seats,
            'total_price': total_price,
            'show_date': show_date,
        })
        email = EmailMessage(subject, message_html, to=[to_email])
        email.content_subtype = "html"
        email.send(fail_silently=True)
    except Exception as e:
        logger.exception("Failed to send booking email: %s", e)

    messages.success(request, "✔ Booking Successful! Ticket sent to your email.")
    return redirect("final", booking_id=booking.b_id)

# ===================== MY BOOKINGS PAGE =====================

def my_bookings(request):
    if "username" not in request.session:
        return redirect("login")

    user = RegisterUser.objects.get(username=request.session['username'])
    bookings = Booking.objects.filter(user=user).order_by('-booked_at')

    # Process each booking to calculate seat types and total seats
    for b in bookings:
        if b.seats:
            # Split seat numbers and convert to integers
            seats = [int(s.strip()) for s in b.seats.split(',')]
            b.total_seats = len(seats)
            # Partition seats
            b.vip_seats = [s for s in seats if s <= 20]
            b.premium_seats = [s for s in seats if 21 <= s <= 60]
            b.regular_seats = [s for s in seats if s > 60]
        else:
            b.total_seats = 0
            b.vip_seats = []
            b.premium_seats = []
            b.regular_seats = []

    context = {"bookings": bookings, "user": user}
    return render(request, "my_bookings.html", context)

# ===================== FINAL TICKET PAGE =====================

def fin(request, booking_id):
    if "username" not in request.session:
        return redirect("/login/?next=/final/")

    booking = get_object_or_404(
        Booking,
        pk=booking_id,
        user__username=request.session["username"]
    )
    return render(request, "final.html", {"booking": booking})

def about(request):
    return render(request,"about.html")

def contact(request):
    return render(request,"contact.html")

def terms(request):
    return render(request,"terms.html")

def privacy(request):
    return render(request,"privacy.html")

def cancel_booking(request, booking_id):
    if "username" not in request.session:
        return redirect("login")

    booking = get_object_or_404(Booking, b_id=booking_id)

    # Check if logged-in user owns the booking
    if booking.user.username != request.session["username"]:
        messages.error(request, "❌ You are not authorized to cancel this booking.")
        return redirect("my_bookings")

    # Move booking to CancelBooking table
    CancelBooking.objects.create(
        user=booking.user,
        movie=booking.movie,
        theatre=booking.theatre,
        show_time=booking.show_time,
        show_date=booking.show_date,
        seats=booking.seats,
        seat_type=booking.seat_type,
        tickets=booking.tickets,
        total_price=booking.total_price,
    )

    # Mark booking as cancelled or delete it
    booking.delete()

    messages.success(request, "✔ Booking cancelled successfully.")
    return redirect("my_bookings")

from django.utils.html import strip_tags

def download_ticket(request, booking_id):
    # ensure user logged in
    if "username" not in request.session:
        return redirect("/login/?next=/final/")

    booking = get_object_or_404(
        Booking,
        pk=booking_id,
        user__username=request.session["username"]
    )

    # Render the same ticket template to HTML (use a template that does NOT include html2pdf JS)
    # I will reuse 'final.html' but it's better to create a separate 'pdf/ticket_pdf.html'
    html_string = render_to_string('final.html', {'booking': booking})

    pdf_bytes = None

    # Try using WeasyPrint if available
    if WEASYPRINT_AVAILABLE:
        out = BytesIO()
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(out)
        pdf_bytes = out.getvalue()
        out.close()
    else:
        # Fallback: create a very simple PDF with Booking info using ReportLab
        # (This is a simple alternative if WeasyPrint not installed)
        try:
            from reportlab.pdfgen import canvas
            out = BytesIO()
            p = canvas.Canvas(out)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, 800, f"Ticket for: {booking.movie.Movie_Name}")
            p.setFont("Helvetica", 12)
            p.drawString(50, 780, f"User: {booking.user.username} ({booking.user.email})")
            p.drawString(50, 760, f"Theatre: {booking.theatre.name}")
            p.drawString(50, 740, f"Show Date: {booking.show_date}")
            p.drawString(50, 720, f"Show Time: {booking.show_time}")
            p.drawString(50, 700, f"Seats: {booking.seats}")
            p.drawString(50, 680, f"Total Price: ₹{booking.total_price}")
            p.showPage()
            p.save()
            pdf_bytes = out.getvalue()
            out.close()
        except Exception:
            pdf_bytes = None

    if not pdf_bytes:
        messages.error(request, "PDF generation failed on server. Please try again.")
        return redirect('final', booking_id=booking.b_id)

    filename = f"Ticket_{booking.b_id}.pdf"

    # Send email with attachment (non-blocking try/except)
    try:
        subject = f"🎟 Your Ticket for {booking.movie.Movie_Name}"
        # render a simple plain/text body and html fallback
        html_message = render_to_string('email/ticket_email.html', {
            'booking': booking,
        })
        plain_message = strip_tags(html_message)

        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
            to=[booking.user.email],
        )
        email.content_subtype = "html"
        email.attach(filename, pdf_bytes, 'application/pdf')
        # send (synchronously). If too slow, we can later move to Celery.
        email.send(fail_silently=True)  # fail_silently True so download won't break
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Failed to send ticket email: %s", e)
        # don't block user download

    # Return PDF as download response
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
