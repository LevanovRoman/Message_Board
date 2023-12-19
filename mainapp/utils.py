import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail


def send_otp(request, email):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=1)
    request.session['otp_valid_date'] = str(valid_date)

    send_mail(
        subject='Code for registration',
        message=f'Code for registration is  {otp}',
        from_email='levanovroman2016@yandex.ru',
        recipient_list=[email,]
    )


