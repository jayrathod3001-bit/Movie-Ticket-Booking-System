from django import forms
from JK.models import RegisterUser

class RegisterForm(forms.ModelForm):
    class Meta:
        model = RegisterUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "gender",
            "phone",
            "email",
            "password1",
            "password2",
            "photo",
        ]

        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Add placeholders and CSS class to each field
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'placeholder': field.label,  # placeholder same as label
                'class': 'form-input'         # optional CSS class for styling
            })
            field.label = ''