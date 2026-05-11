from django.db import models
from django.contrib.auth.models import User

class add_movie(models.Model):
    a_id = models.AutoField(primary_key=True)
    Movie_Name = models.CharField(max_length=200)
    Genre = models.CharField(max_length=100, null=True, blank=True)
    Language = models.CharField(max_length=100, null=True, blank=True)
    Hero = models.CharField(max_length=100, null=True, blank=True)
    Heroine = models.CharField(max_length=100, null=True, blank=True)
    Rating = models.FloatField(default=0)  # default दिया हुआ है इसलिए safe
    Duration = models.CharField(max_length=20, null=True, blank=True)
    Certificate = models.CharField(max_length=10, null=True, blank=True)
    Description = models.TextField(null=True, blank=True)
    Trailer_Link = models.URLField(blank=True, null=True)
    Realese_Date = models.DateField()
    Photo = models.ImageField(upload_to="movies")

    def __str__(self):
        return self.Movie_Name

class coming_movie(models.Model):
    c_id = models.AutoField(primary_key=True)
    C_Name = models.CharField(max_length=200, null=True, blank=True)
    C_Genre = models.CharField(max_length=100, null=True, blank=True)
    C_Language = models.CharField(max_length=100, null=True, blank=True)
    C_Hero = models.CharField(max_length=100, null=True, blank=True)
    C_Heroine = models.CharField(max_length=100, null=True, blank=True)
    C_Rating = models.FloatField(default=0, null=True, blank=True)
    C_Duration = models.CharField(max_length=20, null=True, blank=True)
    C_Certificate = models.CharField(max_length=10, null=True, blank=True)
    C_Description = models.TextField(null=True, blank=True)
    C_Trailer_Link = models.URLField(blank=True, null=True)
    C_Realese_Date = models.DateField(null=True, blank=True)
    C_Photo = models.ImageField(upload_to="movies", null=True, blank=True)

    def __str__(self):
        return self.C_Name

class RegisterUser(models.Model):
    u_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    # Gender choices
    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=gender_choices, blank=True, null=True)

    # Contact Info
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

    # Password
    password1 = models.CharField(max_length=128)
    password2 = models.CharField(max_length=128)

    # Profile Photo
    photo = models.ImageField(upload_to='users/', blank=True, null=True)

    def __str__(self):
        return self.username
    
class Theatre(models.Model):
    t_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    screen = models.CharField(max_length=100)
    facilities = models.CharField(max_length=200)
    show_times = models.CharField(max_length=200, blank=True, default="")
  # ✅ This must exist

    def get_show_times_list(self):
        return [time.strip() for time in self.show_times.split(",")]
    
class Booking(models.Model):
    b_id = models.AutoField(primary_key=True)  # ✅ Unique Booking ID
    user = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(add_movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    show_time = models.CharField(max_length=50)  # e.g., "12:00 PM"
    show_date = models.DateField(null=True, blank=True)
    seats = models.CharField(max_length=200)     # e.g., "A1,A2,A3"
    seat_type = models.CharField(max_length=50, default="Regular")  # e.g., "VIP", "Regular"
    tickets = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    booked_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.movie.Movie_Name} - {self.show_time}"

    def seat_list(self):
        """Return list of seats"""
        return self.seats.split(",")
    
class CancelBooking(models.Model):
    user = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(add_movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    show_date = models.DateField(null=True, blank=True)
    show_time = models.CharField(max_length=50)
    seats = models.CharField(max_length=200)
    seat_type = models.CharField(max_length=50, default="Regular")
    tickets = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancelled - {self.movie.Movie_Name} ({self.user.username})"
