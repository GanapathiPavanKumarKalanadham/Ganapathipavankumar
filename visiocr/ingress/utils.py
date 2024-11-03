import cv2
import pytesseract
import re
from PIL import Image
from django.conf import settings

# Path to your Tesseract-OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import numpy as np

def preprocess_image(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply thresholding
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Save the preprocessed image
    processed_image_path = 'path/to/preprocessed_image.jpg'
    cv2.imwrite(processed_image_path, thresh)

    return processed_image_path

def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='eng')
    return text

def filter_text(text, card_type):
    """Removes unwanted lines from OCR text based on card type."""
    filtered_lines = []
    if card_type == 'PAN':
        unwanted_keywords = ["GOVT. OF INDIA", "INCOME TAX DEPARTMENT", "Permanent Account Number", "Signature"]
    else:
        unwanted_keywords = ["Government of India", "Address", "DOB:", "Male", "Female"]

    for line in text.splitlines():
        if any(keyword in line for keyword in unwanted_keywords) or len(line.strip()) < 3:
            continue
        filtered_lines.append(line.strip())


def extract_pan_details(text):
    """Extract details from a PAN card."""
    pan_details = {}

    # Extract PAN Number
    pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', text)
    if pan_match:
        pan_details['PAN Number'] = pan_match.group(0)

    # Split text into lines for better handling
    lines = text.splitlines()

    # Improved name extraction logic - Name usually appears close to PAN number but not containing certain keywords
    found_pan = False
    for i, line in enumerate(lines):
        # Mark when PAN number is found
        if pan_match and not found_pan and details['PAN Number'] in line:
            found_pan = True
            continue

        # After PAN number is found, search for the name (should be uppercase, skip irrelevant lines)
        if found_pan and line.isupper() and not re.search(r'(INCOME|TAX|DEPARTMENT|GOVT|INDIA|CARD|ACCOUNT)', line):
            pan_details['Name'] = line.strip()
            break

    # Extract Father's Name
    father_match = re.search(r"Father(?:'s)?\s*Name\s*[:\-]?\s*([A-Z\s]+)", text)
    if father_match:
        details["Father's Name"] = father_match.group(1).strip()
    else:
        # Fallback: Search for the line with "Father" and extract the next line
        for i, line in enumerate(lines):
            if "Father" in line:
                if i + 1 < len(lines):
                    pan_details["Father's Name"] = lines[i + 1].strip()
                    break

    # Extract Date of Birth
    dob_match = re.search(r'(\d{2}[\/\-]\d{2}[\/\-]\d{4})', text)
    if dob_match:
        pan_details['Date of Birth'] = dob_match.group(1)

    return pan_details

def extract_aadhaar_details(text):
    aadhaar_details = {}

    # Regex patterns to extract Aadhaar details
    aadhaar_pattern = r"(\d{4} \d{4} \d{4})"
    name_pattern = r"(?<=Name\s)([A-Z\s]+)"
    dob_pattern = r"DOB:\s*(\d{2}-\d{2}-\d{4})"
    gender_pattern = r"Gender:\s*(\w+)"

    # Extracting Aadhaar number
    aadhaar_match = re.search(aadhaar_pattern, text)
    if aadhaar_match:
        aadhaar_details['Aadhaar Number'] = aadhaar_match.group(0)

    # Extracting Name
    name_match = re.search(name_pattern, text)
    if name_match:
        aadhaar_details['Name'] = name_match.group(0).strip()

    # Extracting Date of Birth
    dob_match = re.search(dob_pattern, text)
    if dob_match:
        aadhaar_details['Date of Birth'] = dob_match.group(0)

    # Extracting Gender
    gender_match = re.search(gender_pattern, text)
    if gender_match:
        aadhaar_details['Gender'] = gender_match.group(0)

    return aadhaar_details


def extract_and_filter_details(image_path):
    """Determine card type and extract relevant details."""
    processed_image_path = preprocess_image(image_path)
    raw_text = extract_text_from_image(processed_image_path)

    # Check for card type
    if re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', pan_details):
        card_type = 'PAN'
        filtered_text = filter_text(processed_image_path, card_type)
        details = extract_pan_details(filtered_text)
    elif re.search(r'\d{4}\s?\d{4}\s?\d{4}', aadhaar_details):
        card_type = 'Aadhaar'
        filtered_text = filter_text(processed_image_path, card_type)
        details = extract_aadhaar_details(filtered_text)
    else:
        card_type = 'Unknown'
        details = {}

    return card_type, details

def process_image_and_extract_details(image_path, card_type):
    """Preprocess the image and extract details based on the card type."""
    # Preprocess the image
    processed_image_path = preprocess_image(image_path)
    
    # Extract text from the processed image
    text = extract_text_from_image(processed_image_path)
    
    if card_type == 'PAN':
        return extract_pan_details(text)
    elif card_type == 'Aadhaar':
        return extract_aadhaar_details(text)