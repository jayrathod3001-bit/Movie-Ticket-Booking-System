from django.contrib import admin
from JK.models import Booking,add_movie,coming_movie,RegisterUser,Theatre,CancelBooking

class AddMovie(admin.ModelAdmin):
    list_display = ('a_id','Movie_Name','Genre','Language','Hero','Heroine','Rating','Duration','Certificate','Description','Realese_Date')

class ComingMovie(admin.ModelAdmin):
    list_display = ('c_id','C_Name','C_Genre','C_Language','C_Hero','C_Heroine','C_Rating','C_Duration','C_Certificate','C_Description','C_Realese_Date')

class RegisterUserAdmin(admin.ModelAdmin):
    list_display = ("u_id", "username","first_name","last_name","birth_date","gender","phone", "email", "password1", "password2")

class AddTheatre(admin.ModelAdmin):
    list_display = ("t_id","name","address","screen","facilities","show_times")

class AddBooking(admin.ModelAdmin):
    list_display = ("b_id","user","movie","theatre","show_date","show_time","seats","seat_type","tickets","total_price","booked_at","is_paid")

class Cancel(admin.ModelAdmin):
    list_display = ("user","movie","theatre","show_date","show_time","seats","seat_type","tickets","total_price","cancelled_at")

admin.site.register(add_movie,AddMovie)
admin.site.register(coming_movie,ComingMovie)
admin.site.register(RegisterUser,RegisterUserAdmin)
admin.site.register(Theatre,AddTheatre)
admin.site.register(Booking,AddBooking)
admin.site.register(CancelBooking,Cancel)