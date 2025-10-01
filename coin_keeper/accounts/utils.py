from django.core import signing, exceptions

def genera_token(user_id):
    return signing.dumps({"user_id": user_id})

def verifica_token(token, max_age=3600):
    try:
        data = signing.loads(token, max_age=max_age)
        return data["user_id"]
    except (exceptions.BadSignature, exceptions.SignatureExpired):
        return None
