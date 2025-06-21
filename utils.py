import os
import requests
import secrets
from datetime import datetime, timedelta
from PIL import Image
from werkzeug.utils import secure_filename
from app import app

def get_weather_data(lat, lon):
    """Fetch weather data from OpenWeatherMap API"""
    api_key = os.environ.get('OPENWEATHER_API_KEY', 'demo_key')
    if api_key == 'demo_key':
        # Return mock data when API key is not available
        return {
            'current': {
                'temp': 22,
                'description': 'Clear sky',
                'icon': '01d',
                'humidity': 65,
                'wind_speed': 3.5
            },
            'forecast': [
                {'date': 'Today', 'temp_max': 25, 'temp_min': 18, 'icon': '01d'},
                {'date': 'Tomorrow', 'temp_max': 23, 'temp_min': 16, 'icon': '02d'},
                {'date': 'Day 3', 'temp_max': 24, 'temp_min': 17, 'icon': '03d'}
            ]
        }
    
    try:
        # Current weather
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        current_response = requests.get(current_url, timeout=10)
        current_data = current_response.json()
        
        # 3-day forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_data = forecast_response.json()
        
        # Process forecast data (get daily forecasts)
        daily_forecasts = []
        current_date = None
        for item in forecast_data['list'][:9]:  # Next 3 days (3 items per day)
            date_obj = datetime.fromtimestamp(item['dt'])
            date_str = date_obj.strftime('%a, %b %d')
            if date_str != current_date:
                current_date = date_str
                daily_forecasts.append({
                    'date': date_str,
                    'temp_max': int(item['main']['temp_max']),
                    'temp_min': int(item['main']['temp_min']),
                    'icon': item['weather'][0]['icon']
                })
                if len(daily_forecasts) >= 3:
                    break
        
        return {
            'current': {
                'temp': int(current_data['main']['temp']),
                'description': current_data['weather'][0]['description'].title(),
                'icon': current_data['weather'][0]['icon'],
                'humidity': current_data['main']['humidity'],
                'wind_speed': current_data['wind']['speed']
            },
            'forecast': daily_forecasts
        }
    
    except Exception as e:
        app.logger.error(f"Weather API error: {str(e)}")
        return None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_uploaded_file(file, folder='uploads'):
    """Save uploaded file with secure filename"""
    if file and allowed_file(file.filename):
        # Generate secure filename
        filename = secure_filename(file.filename)
        unique_filename = secrets.token_hex(8) + '_' + filename
        
        # Ensure upload directory exists
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Resize image if it's too large
        try:
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if larger than 1200x1200
                if img.width > 1200 or img.height > 1200:
                    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    img.save(file_path, optimize=True, quality=85)
        except Exception as e:
            app.logger.error(f"Image processing error: {str(e)}")
        
        return os.path.join(folder, unique_filename)
    return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def format_date_nepali(date_obj):
    """Format date for display (could be extended for Nepali calendar)"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%B %d, %Y')
    elif hasattr(date_obj, 'strftime'):
        return date_obj.strftime('%B %d, %Y')
    return str(date_obj)

def generate_google_maps_url(lat, lon, name=""):
    """Generate Google Maps URL for directions"""
    if name:
        query = f"{name}/@{lat},{lon}"
    else:
        query = f"{lat},{lon}"
    return f"https://www.google.com/maps/search/?api=1&query={query}"

def award_points(user, action):
    """Award points to user for various actions"""
    points_map = {
        'review': 10,
        'photo_upload': 5,
        'spot_add': 20,
        'tip_share': 5,
        'road_update': 5
    }
    
    if action in points_map:
        user.points += points_map[action]
        user.update_badge()

def get_districts():
    """Get list of districts in Nepal"""
    return [
        'Achham', 'Arghakhanchi', 'Baglung', 'Baitadi', 'Bajhang', 'Bajura',
        'Banke', 'Bara', 'Bardiya', 'Bhaktapur', 'Bhojpur', 'Chitwan',
        'Dadeldhura', 'Dailekh', 'Dang', 'Darchula', 'Dhading', 'Dhankuta',
        'Dhanusa', 'Dolakha', 'Dolpa', 'Doti', 'Gorkha', 'Gulmi',
        'Humla', 'Ilam', 'Jajarkot', 'Jhapa', 'Jumla', 'Kailali',
        'Kalikot', 'Kanchanpur', 'Kapilvastu', 'Kaski', 'Kathmandu',
        'Kavrepalanchok', 'Khotang', 'Lalitpur', 'Lamjung', 'Mahottari',
        'Makwanpur', 'Manang', 'Morang', 'Mugu', 'Mustang', 'Myagdi',
        'Nawalparasi', 'Nuwakot', 'Okhaldhunga', 'Palpa', 'Panchthar',
        'Parbat', 'Parsa', 'Pyuthan', 'Ramechhap', 'Rasuwa', 'Rautahat',
        'Rolpa', 'Rukum', 'Rupandehi', 'Salyan', 'Sankhuwasabha', 'Saptari',
        'Sarlahi', 'Sindhuli', 'Sindhupalchok', 'Siraha', 'Solukhumbu',
        'Sunsari', 'Surkhet', 'Syangja', 'Tanahu', 'Taplejung', 'Terhathum',
        'Udayapur'
    ]
