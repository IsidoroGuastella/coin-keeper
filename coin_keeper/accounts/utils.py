import re
import dns.resolver
from django.core import signing, exceptions
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _




def genera_token(user_id):
    return signing.dumps({"user_id": user_id})

def verifica_token(token, max_age=3600):
    try:
        data = signing.loads(token, max_age=max_age)
        return data["user_id"]
    except (exceptions.BadSignature, exceptions.SignatureExpired):
        return None

def validate_email_mx(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValidationError(_("Formato email non valido."))

    dominio = email.split("@")[1]
    try:
        dns.resolver.resolve(dominio, "MX")
    except Exception:
        raise ValidationError(_("Il dominio dell'email non esiste o non riceve posta."))
