from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
import hashlib
import random
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def generate_token(request):
    try:
        data = json.loads(request.body)
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        scope = data.get('scope')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("SELECT scope FROM public.user WHERE client_id = %s AND client_secret = %s", [client_id, client_secret])
        user = cursor.fetchone()
        if user and scope in user[0]:
            access_token = hashlib.md5(str(random.random()).encode()).hexdigest()[:22]
            expiration_time = timezone.now() + timezone.timedelta(hours=2)
            cursor.execute(
                "INSERT INTO public.token (client_id, access_scope, access_token, expiration_time) VALUES (%s, %s, %s, %s)",
                [client_id, [scope], access_token, expiration_time]
            )
            return JsonResponse({
                "access_token": access_token,
                "expires_in": 7200,
                "refresh_token": "",
                "scope": scope,
                "security_level": "normal",
                "token_type": "Bearer"
            })
        else:
            return JsonResponse({"error": "Invalid client credentials or scope"}, status=401)
@csrf_exempt
def check_token(request):
    token = request.headers.get('Authorization').split()[1]

    with connection.cursor() as cursor:
        cursor.execute("SELECT access_scope FROM public.token WHERE access_token = %s AND expiration_time > %s", [token, timezone.now()])
        token_data = cursor.fetchone()
        if token_data:
            return JsonResponse({"scope": token_data[0]})
        else:
            return JsonResponse({"error": "Token expired or invalid"}, status=401)
        