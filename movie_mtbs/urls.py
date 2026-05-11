from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

# Import your views (adjust path if your project structure differs)
from movie_mtbs.view import (
    renderpage, timing, fin, seat, payment,
    register_view, login_view, logout_view,
    view_profile, update_profile, movie_detail,
    my_bookings, download_ticket, confirm_booking,
    about, contact, terms, privacy, cancel_booking
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', renderpage, name="home"),                      # optional: root -> home
    path('home/', renderpage, name="home"),
    path('about/', about, name="about"),
    path('contact/', contact, name="contact"),
    path('terms/', terms, name="terms"),
    path('privacy/', privacy, name="privacy"),
    path("movie/<int:movie_id>/", movie_detail, name="movie_detail"),
    path('timing/', timing, name="timing"),                # name fixed to 'timing'
    path('seat/', seat, name="seat"),
    path('payment/', payment, name="payment"),
    path('confirm-booking/', confirm_booking, name='confirm_booking'),
    path('final/<int:booking_id>/', fin, name="final"),
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('profile/', view_profile, name='view_profile'),
    path('update-profile/', update_profile, name='update_profile'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path('download_ticket/<int:booking_id>/', download_ticket, name='download_ticket'),
    path("cancel-booking/<int:booking_id>/", cancel_booking, name="cancel_booking"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
