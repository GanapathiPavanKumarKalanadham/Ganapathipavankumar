from django.shortcuts import render, redirect
from . import views
from django.http import HttpResponse
import random
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import numpy as np
import cv2
import pytesseract
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render
from .utils import process_image_and_extract_details  # Make sure to import the new function
from django.http import JsonResponse
from .utils import preprocess_image, extract_text_from_image, extract_pan_details, extract_aadhaar_details

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        image_path = f'media/{file.name}'  # Save uploaded file temporarily

        # Save the uploaded image to a media directory
        with open(image_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Preprocess the uploaded image
        processed_image_path = preprocess_image(image_path)
        text = extract_text_from_image(processed_image_path)

        # Extract details based on keywords in the text
        if 'PAN' in text:  # Logic to determine if the uploaded file is PAN or Aadhaar
            details = extract_pan_details(text)
            card_type = 'PAN'
        elif 'Aadhaar' in text:  # Adjust this based on your actual text to identify Aadhaar
            details = extract_aadhaar_details(text)
            card_type = 'Aadhaar'
        else:
            return JsonResponse({"error": "Unable to identify card type."}, status=400)

        # Validate and insert into the database
        if validate_details(details, card_type):
            insert_details(details, card_type)
            return JsonResponse({"details": details}, status=200)
        else:
            return JsonResponse({"error": "Invalid card details."}, status=400)

    return render(request, 'upload.html')


def ocr_process(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        image_path = f"uploads/{image_file.name}"  # Save the uploaded file to the media folder

        # Save the image
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Process the image
        processed_image_path = preprocess_image(image_path)
        text = extract_text_from_image(processed_image_path)

        # Check for PAN or Aadhaar card by looking for specific patterns in the text
        pan_details = extract_pan_details(text)
        aadhaar_details = extract_aadhaar_details(text)

        response_data = {}

        # Validate and insert PAN details
        if pan_details and validate_details(pan_details, 'PAN'):
            insert_details(pan_details, 'PAN')
            response_data['PAN Details'] = pan_details
        else:
            response_data['PAN Error'] = "No valid PAN details found."

        # Validate and insert Aadhaar details
        if aadhaar_details and validate_details(aadhaar_details, 'Aadhaar'):
            insert_details(aadhaar_details, 'Aadhaar')
            response_data['Aadhaar Details'] = aadhaar_details
        else:
            response_data['Aadhaar Error'] = "No valid Aadhaar details found."

        # Clean up: You may want to remove the processed image files after processing
        # os.remove(image_path)
        # os.remove(processed_image_path)

        return JsonResponse(response_data)

    return render(request, 'ingress/home.html')


def home(request):
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')


def process_ocr(request):
    if request.method == 'POST' and request.FILES.get('document'):
        # Retrieve uploaded file
        uploaded_file = request.FILES['document']
        
        # Read image file into OpenCV
        file_data = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_data, cv2.IMREAD_COLOR)
        
        # OCR processing
        extracted_text = pytesseract.image_to_string(image)
        
        # Render the extracted text to display to the user
        return render(request, 'display_text.html', {'extracted_text': extracted_text})
    
    return HttpResponse("Invalid request")


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, 'Account created successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Change 'home' to your desired redirect page
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ingress/views.py


def upload_view(request):
    if request.method == 'POST':
        # Check if a file was uploaded
        uploaded_file = request.FILES.get('file')
        
        if uploaded_file:
            # Validate file type (optional)
            if uploaded_file.content_type in ['image/jpeg', 'image/png', 'application/pdf']:  # Add allowed types
                # Save the file
                fs = FileSystemStorage()
                filename = fs.save(uploaded_file.name, uploaded_file)  # Save with original name
                file_url = fs.url(filename)  # Get the URL of the saved file

                # Optionally, process the file (e.g., run OCR)
                # process_file(file_url)

                # Render a success page or return a success response
                return render(request, 'upload_success.html', {'file_url': file_url})
            else:
                return render(request, 'upload.html', {'error': 'Unsupported file type. Please upload a JPEG, PNG, or PDF.'})
        else:
            return render(request, 'upload.html', {'error': 'No file uploaded. Please select a file to upload.'})

    return render(request, 'upload.html')  # Show the upload form for GET requests




def extract_details_view(request):
    if request.method == "POST" and request.FILES['image']:
        image = request.FILES['image']
        # Save the image temporarily
        image_path = 'temp_image.jpg'  # You can modify this to a more appropriate path
        with open(image_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Process the image
        processed_image_path = preprocess_image(image_path)
        text = extract_text_from_image(processed_image_path)
        pan_details = extract_pan_details(text)

        # Prepare the context with only the required details
        context = {
            'name': pan_details.get('Name'),
            "father_name": pan_details.get("Father's Name"),
            'dob': pan_details.get('Date of Birth'),
        }

        return render(request, 'extract_details.html', context)

    return render(request, 'upload_image.html')  # Render an upload form if not a POST request


def extract_details_view(request):
    return render(request, 'extract_details.html')