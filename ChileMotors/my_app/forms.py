from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DatosPersonales, Contacto
from django.core.mail import send_mail
from ChileMotors.settings import EMAIL_HOST_USER  # Asegúrate de importar tu configuración de email


class CustomUserCreationForm(UserCreationForm):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    email = forms.EmailField()
    telefono = forms.CharField(max_length=15)
    direccion = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'nombre', 'apellido', 'email', 'telefono', 'direccion', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            datos_personales = DatosPersonales.objects.create(
                user=user,
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                email=self.cleaned_data['email'],
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion']
            )

            # Enviar correo electrónico
            subject = "Registro exitoso en ChileMotors"
            message = (
                f"Estimado {datos_personales.nombre},\n\n"
                "¡Gracias por registrarte en ChileMotors! Nos alegra tenerte con nosotros.\n\n"
                "Saludos,\nChileMotors"
            )
            recipient = datos_personales.email

            send_mail(subject, message, EMAIL_HOST_USER, [recipient])

        return user

class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        fields = ['nombre', 'apellido', 'email', 'telefono']

class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'apellido', 'email', 'telefono', 'detalle']

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']
    
    metodo_pago = forms.ChoiceField(choices=[('efectivo', 'Efectivo'), ('debito', 'Débito')], widget=forms.RadioSelect)