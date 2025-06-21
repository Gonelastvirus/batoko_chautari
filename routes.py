import os
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, NatureSpot, Review, Photo, Visit, Bookmark, CommunityTip, RoadUpdate
from forms import (LoginForm, RegistrationForm, ReviewForm, SpotFilterForm, AddSpotForm, 
                  CommunityTipForm, RoadUpdateForm, ProfileEditForm)
from utils import (get_weather_data, save_uploaded_file, calculate_distance, 
                  format_date_nepali, generate_google_maps_url, award_points, get_districts)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, 
                   full_name=form.full_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Main routes
@app.route('/')
def index():
    # Get featured spots (highest rated, most visited)
    featured_spots = db.session.query(NatureSpot).filter_by(is_verified=True).limit(6).all()
    
    # Get recent reviews with photos
    recent_reviews = db.session.query(Review).join(Photo).filter(
        Photo.is_approved == True
    ).order_by(Review.created_at.desc()).limit(3).all()
    
    # Get top contributors
    top_contributors = db.session.query(User).order_by(User.points.desc()).limit(5).all()
    
    context = {
        'featured_spots': featured_spots,
        'recent_reviews': recent_reviews,
        'top_contributors': top_contributors
    }
    
    return render_template('index.html', **context)

@app.route('/discover')
def discover():
    form = SpotFilterForm()
    
    # Populate district choices
    districts = get_districts()
    form.district.choices = [('', 'All Districts')] + [(d, d) for d in districts]
    
    # Base query
    query = NatureSpot.query.filter_by(is_verified=True)
    
    # Apply filters
    if request.args.get('district'):
        query = query.filter(NatureSpot.district == request.args.get('district'))
    
    if request.args.get('spot_type'):
        query = query.filter(NatureSpot.spot_type == request.args.get('spot_type'))
    
    if request.args.get('difficulty'):
        query = query.filter(NatureSpot.difficulty_level == request.args.get('difficulty'))
    
    # Search functionality
    search_query = request.args.get('search')
    if search_query:
        query = query.filter(NatureSpot.name.contains(search_query))
    
    # Sort options
    sort_by = request.args.get('sort', 'name')
    if sort_by == 'rating':
        spots = query.all()
        spots.sort(key=lambda x: x.get_average_rating(), reverse=True)
    elif sort_by == 'recent':
        spots = query.order_by(NatureSpot.created_at.desc()).all()
    else:
        spots = query.order_by(NatureSpot.name).all()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 12
    start = (page - 1) * per_page
    end = start + per_page
    spots_paginated = spots[start:end]
    
    has_next = len(spots) > end
    has_prev = page > 1
    
    return render_template('discover.html', spots=spots_paginated, form=form,
                         has_next=has_next, has_prev=has_prev, page=page,
                         total_spots=len(spots))

@app.route('/spot/<int:id>')
def spot_detail(id):
    spot = NatureSpot.query.get_or_404(id)
    
    # Get weather data
    weather = get_weather_data(spot.latitude, spot.longitude)
    
    # Get reviews with pagination
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(nature_spot_id=id).order_by(
        Review.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False)
    
    # Get approved photos
    photos = Photo.query.filter_by(nature_spot_id=id, is_approved=True).order_by(
        Photo.is_cover_photo.desc(), Photo.created_at.desc()).all()
    
    # Get community tips
    tips = CommunityTip.query.filter_by(nature_spot_id=id, is_approved=True).order_by(
        CommunityTip.created_at.desc()).all()
    
    # Check if user has visited
    user_visited = False
    user_bookmarked = False
    if current_user.is_authenticated:
        user_visited = Visit.query.filter_by(user_id=current_user.id, nature_spot_id=id).first() is not None
        user_bookmarked = Bookmark.query.filter_by(user_id=current_user.id, nature_spot_id=id).first() is not None
    
    # Generate Google Maps URL
    maps_url = generate_google_maps_url(spot.latitude, spot.longitude, spot.name)
    
    return render_template('spot_detail.html', spot=spot, weather=weather,
                         reviews=reviews, photos=photos, tips=tips,
                         user_visited=user_visited, user_bookmarked=user_bookmarked,
                         maps_url=maps_url)

@app.route('/add_review/<int:spot_id>', methods=['GET', 'POST'])
@login_required
def add_review(spot_id):
    spot = NatureSpot.query.get_or_404(spot_id)
    
    # Check if user has already reviewed this spot
    existing_review = Review.query.filter_by(user_id=current_user.id, nature_spot_id=spot_id).first()
    if existing_review:
        flash('You have already reviewed this spot.', 'warning')
        return redirect(url_for('spot_detail', id=spot_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        # Create review
        review = Review(
            user_id=current_user.id,
            nature_spot_id=spot_id,
            rating=form.rating.data,
            comment=form.comment.data,
            visit_date=form.visit_date.data
        )
        db.session.add(review)
        db.session.flush()  # Get review ID
        
        # Handle photo uploads
        photos_uploaded = 0
        if 'photos' in request.files:
            files = request.files.getlist('photos')
            for file in files:
                if file and file.filename:
                    photo_path = save_uploaded_file(file, 'reviews')
                    if photo_path:
                        photo = Photo(
                            user_id=current_user.id,
                            nature_spot_id=spot_id,
                            review_id=review.id,
                            filename=photo_path,
                            original_filename=file.filename
                        )
                        db.session.add(photo)
                        photos_uploaded += 1
        
        # Record visit
        visit = Visit(user_id=current_user.id, nature_spot_id=spot_id, 
                     visit_date=form.visit_date.data, has_reviewed=True)
        db.session.add(visit)
        
        # Award points
        award_points(current_user, 'review')
        if photos_uploaded > 0:
            award_points(current_user, 'photo_upload')
        
        db.session.commit()
        
        flash(f'Thank you for your review! You earned {10 + (5 if photos_uploaded > 0 else 0)} points.', 'success')
        return redirect(url_for('spot_detail', id=spot_id))
    
    return render_template('add_review.html', form=form, spot=spot)

@app.route('/profile')
@app.route('/profile/<username>')
@login_required
def profile(username=None):
    if username:
        user = User.query.filter_by(username=username).first_or_404()
    else:
        user = current_user
    
    # Get user's visits and reviews
    visits = Visit.query.filter_by(user_id=user.id).order_by(Visit.visit_date.desc()).all()
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()
    bookmarks = Bookmark.query.filter_by(user_id=user.id).order_by(Bookmark.created_at.desc()).all()
    
    # Get user's photos
    photos = Photo.query.filter_by(user_id=user.id, is_approved=True).order_by(
        Photo.created_at.desc()).limit(12).all()
    
    # Calculate statistics
    stats = {
        'total_visits': len(visits),
        'total_reviews': len(reviews),
        'total_photos': Photo.query.filter_by(user_id=user.id, is_approved=True).count(),
        'total_bookmarks': len(bookmarks)
    }
    
    return render_template('profile.html', user=user, visits=visits, reviews=reviews,
                         bookmarks=bookmarks, photos=photos, stats=stats)

@app.route('/bookmark/<int:spot_id>')
@login_required
def bookmark_spot(spot_id):
    spot = NatureSpot.query.get_or_404(spot_id)
    
    existing_bookmark = Bookmark.query.filter_by(user_id=current_user.id, nature_spot_id=spot_id).first()
    
    if existing_bookmark:
        db.session.delete(existing_bookmark)
        flash('Bookmark removed.', 'info')
    else:
        bookmark = Bookmark(user_id=current_user.id, nature_spot_id=spot_id)
        db.session.add(bookmark)
        flash('Spot bookmarked!', 'success')
    
    db.session.commit()
    return redirect(url_for('spot_detail', id=spot_id))

@app.route('/add_tip/<int:spot_id>', methods=['POST'])
@login_required
def add_tip(spot_id):
    spot = NatureSpot.query.get_or_404(spot_id)
    form = CommunityTipForm()
    
    if form.validate_on_submit():
        tip = CommunityTip(
            user_id=current_user.id,
            nature_spot_id=spot_id,
            tip_type=form.tip_type.data,
            content=form.content.data
        )
        db.session.add(tip)
        award_points(current_user, 'tip_share')
        db.session.commit()
        
        flash('Your tip has been shared! Thank you for contributing.', 'success')
    else:
        flash('Error sharing tip. Please check your input.', 'danger')
    
    return redirect(url_for('spot_detail', id=spot_id))

@app.route('/update_road/<int:spot_id>', methods=['POST'])
@login_required
def update_road(spot_id):
    spot = NatureSpot.query.get_or_404(spot_id)
    form = RoadUpdateForm()
    
    if form.validate_on_submit():
        road_update = RoadUpdate(
            user_id=current_user.id,
            nature_spot_id=spot_id,
            status=form.status.data,
            description=form.description.data
        )
        db.session.add(road_update)
        
        # Update spot's road status
        spot.road_status = form.status.data
        spot.last_road_update = datetime.utcnow()
        
        award_points(current_user, 'road_update')
        db.session.commit()
        
        flash('Road status updated! Thank you for keeping the community informed.', 'success')
    else:
        flash('Error updating road status. Please check your input.', 'danger')
    
    return redirect(url_for('spot_detail', id=spot_id))

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/leaderboard')
def leaderboard():
    # Get top contributors
    top_users = User.query.order_by(User.points.desc()).limit(50).all()
    
    # Get top reviewers (by number of reviews)
    top_reviewers = db.session.query(User).join(Review).group_by(User.id).order_by(
        db.func.count(Review.id).desc()).limit(20).all()
    
    # Get top photographers (by approved photos)
    top_photographers = db.session.query(User).join(Photo).filter(
        Photo.is_approved == True).group_by(User.id).order_by(
        db.func.count(Photo.id).desc()).limit(20).all()
    
    return render_template('leaderboard.html', top_users=top_users,
                         top_reviewers=top_reviewers, top_photographers=top_photographers)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'total_spots': NatureSpot.query.count(),
        'total_reviews': Review.query.count(),
        'pending_photos': Photo.query.filter_by(is_approved=False).count(),
        'total_visits': Visit.query.count()
    }
    
    # Get recent activity
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    pending_photos = Photo.query.filter_by(is_approved=False).order_by(Photo.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats,
                         recent_reviews=recent_reviews, pending_photos=pending_photos)

@app.route('/admin/approve_photos')
@login_required
def approve_photos():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    photos = Photo.query.filter_by(is_approved=False).order_by(
        Photo.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/approve_photos.html', photos=photos)

@app.route('/admin/approve_photo/<int:photo_id>')
@login_required
def approve_photo(photo_id):
    if not current_user.is_admin:
        abort(403)
    
    photo = Photo.query.get_or_404(photo_id)
    photo.is_approved = True
    photo.approved_at = datetime.utcnow()
    db.session.commit()
    
    flash('Photo approved!', 'success')
    return redirect(url_for('approve_photos'))

@app.route('/admin/reject_photo/<int:photo_id>')
@login_required
def reject_photo(photo_id):
    if not current_user.is_admin:
        abort(403)
    
    photo = Photo.query.get_or_404(photo_id)
    
    # Delete the file
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        app.logger.error(f"Error deleting file: {str(e)}")
    
    db.session.delete(photo)
    db.session.commit()
    
    flash('Photo rejected and deleted.', 'info')
    return redirect(url_for('approve_photos'))

# API routes for AJAX calls
@app.route('/api/weather/<float:lat>/<float:lon>')
def api_weather(lat, lon):
    weather_data = get_weather_data(lat, lon)
    if weather_data:
        return jsonify(weather_data)
    return jsonify({'error': 'Weather data unavailable'}), 404

# Static file serving
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Template filters
@app.template_filter('format_date')
def format_date_filter(date_obj):
    return format_date_nepali(date_obj)

@app.template_filter('stars')
def stars_filter(rating):
    """Convert rating to star display"""
    stars = '★' * int(rating) + '☆' * (5 - int(rating))
    return stars

# Context processors
@app.context_processor
def inject_forms():
    """Inject forms that are used across multiple templates"""
    tip_form = CommunityTipForm()
    road_form = RoadUpdateForm()
    return dict(tip_form=tip_form, road_form=road_form)

@app.context_processor
def inject_constants():
    """Inject constants for templates"""
    return dict(
        SPOT_TYPES=['hill', 'lake', 'forest', 'waterfall', 'cave', 'valley'],
        DIFFICULTY_LEVELS=['easy', 'moderate', 'hard'],
        ROAD_STATUS_COLORS={
            'smooth': 'success',
            'damaged': 'warning', 
            'construction': 'info',
            'landslide': 'danger',
            'unknown': 'secondary'
        }
    )
