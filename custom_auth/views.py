from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
import json

@ensure_csrf_cookie
def get_csrf(request):
    print("Cookies:", request.COOKIES)
    # set cookie csrf in navigateur
    return JsonResponse({"detail": "CSRF cookie set"})

@csrf_protect
def login(request):
    #check if request POST
    if request.method != "POST":
        return JsonResponse({"error": f"Not a POST, got {request.method}"}, status=405)

    try:
        data = json.loads(request.body) #get data from front
        print("EMAIL:", data.get("email"))
        return JsonResponse({"message": "Login success"})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)