#!/usr/bin/env python3
"""
Add sample data to the Batoko Chautari database
This script populates the database with sample nature spots, users, and reviews
"""

from app import app, db
from models import User, NatureSpot, Review, Photo, Visit, Bookmark, CommunityTip
from datetime import datetime, date
import random

def create_sample_data():
    with app.app_context():
        # Create sample users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@batokochautari.com',
                'full_name': 'Admin User',
                'password': 'admin123',
                'is_admin': True,
                'points': 1000,
                'bio': 'Administrator of Batoko Chautari platform'
            },
            {
                'username': 'ramesh_hiker',
                'email': 'ramesh@example.com',
                'full_name': 'Ramesh Shrestha',
                'password': 'password123',
                'points': 450,
                'bio': 'Mountain enthusiast from Kathmandu. Love exploring hidden trails!'
            },
            {
                'username': 'sita_explorer',
                'email': 'sita@example.com',
                'full_name': 'Sita Gurung',
                'password': 'password123',
                'points': 320,
                'bio': 'Nature photographer and travel blogger from Pokhara'
            },
            {
                'username': 'bikash_trekker',
                'email': 'bikash@example.com',
                'full_name': 'Bikash Tamang',
                'password': 'password123',
                'points': 275,
                'bio': 'Professional trekking guide with 10+ years experience'
            }
        ]

        print("Creating sample users...")
        for user_data in users_data:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    is_admin=user_data.get('is_admin', False),
                    points=user_data['points'],
                    bio=user_data['bio']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
        
        db.session.commit()

        # Create sample nature spots
        spots_data = [
            {
                'name': 'Nagarkot Sunrise Point',
                'description': 'Famous for its panoramic sunrise views over the Himalayas including Mount Everest on clear days. Located on a hilltop at 2,175m altitude.',
                'district': 'Kathmandu',
                'latitude': 27.7172,
                'longitude': 85.5222,
                'altitude': 2175,
                'spot_type': 'hill',
                'difficulty_level': 'easy',
                'best_season': 'October to March',
                'entry_fee': 0,
                'is_verified': True,
                'road_status': 'smooth'
            },
            {
                'name': 'Phewa Lake',
                'description': 'Pristine freshwater lake in Pokhara with stunning reflections of the Annapurna range. Perfect for boating and peaceful meditation.',
                'district': 'Pokhara',
                'latitude': 28.2096,
                'longitude': 83.9856,
                'altitude': 742,
                'spot_type': 'lake',
                'difficulty_level': 'easy',
                'best_season': 'Year round',
                'entry_fee': 50,
                'is_verified': True,
                'road_status': 'smooth'
            },
            {
                'name': 'Sekumpana Waterfall',
                'description': 'Hidden gem waterfall in Dolakha district. Requires a moderate hike through beautiful rhododendron forests.',
                'district': 'Dolakha',
                'latitude': 27.8125,
                'longitude': 86.1869,
                'altitude': 1650,
                'spot_type': 'waterfall',
                'difficulty_level': 'moderate',
                'best_season': 'March to May, September to November',
                'entry_fee': 0,
                'is_verified': True,
                'road_status': 'damaged'
            },
            {
                'name': 'Chitwan National Park',
                'description': 'UNESCO World Heritage site famous for wildlife including Bengal tigers, one-horned rhinoceros, and diverse bird species.',
                'district': 'Chitwan',
                'latitude': 27.5291,
                'longitude': 84.3542,
                'altitude': 150,
                'spot_type': 'forest',
                'difficulty_level': 'easy',
                'best_season': 'October to March',
                'entry_fee': 2000,
                'is_verified': True,
                'road_status': 'smooth'
            },
            {
                'name': 'Kathmandu Valley Viewpoint',
                'description': 'Spectacular viewpoint overlooking the entire Kathmandu valley. Best visited during clear weather for panoramic city views.',
                'district': 'Lalitpur',
                'latitude': 27.6588,
                'longitude': 85.3247,
                'altitude': 1800,
                'spot_type': 'hill',
                'difficulty_level': 'moderate',
                'best_season': 'October to February',
                'entry_fee': 0,
                'is_verified': True,
                'road_status': 'construction'
            },
            {
                'name': 'Rara Lake',
                'description': 'Nepal\'s largest lake located in the remote far west. Crystal clear blue waters surrounded by pristine mountains.',
                'district': 'Other',
                'latitude': 29.5200,
                'longitude': 82.0814,
                'altitude': 2990,
                'spot_type': 'lake',
                'difficulty_level': 'hard',
                'best_season': 'April to November',
                'entry_fee': 3000,
                'is_verified': True,
                'road_status': 'landslide'
            }
        ]

        print("Creating sample nature spots...")
        for spot_data in spots_data:
            existing_spot = NatureSpot.query.filter_by(name=spot_data['name']).first()
            if not existing_spot:
                spot = NatureSpot(**spot_data)
                db.session.add(spot)
        
        db.session.commit()

        # Create sample reviews
        users = User.query.all()
        spots = NatureSpot.query.all()
        
        reviews_data = [
            {
                'user_username': 'ramesh_hiker',
                'spot_name': 'Nagarkot Sunrise Point',
                'rating': 5,
                'comment': 'Absolutely breathtaking sunrise views! The road is good and facilities are decent. Highly recommended for early morning trips.',
                'visit_date': date(2024, 11, 15)
            },
            {
                'user_username': 'sita_explorer',
                'spot_name': 'Phewa Lake',
                'rating': 4,
                'comment': 'Beautiful lake with amazing mountain reflections. Perfect for photography. The boat ride is relaxing.',
                'visit_date': date(2024, 10, 22)
            },
            {
                'user_username': 'bikash_trekker',
                'spot_name': 'Sekumpana Waterfall',
                'rating': 4,
                'comment': 'Worth the hike! The waterfall is stunning especially during monsoon. Trail can be slippery so bring proper shoes.',
                'visit_date': date(2024, 9, 8)
            },
            {
                'user_username': 'ramesh_hiker',
                'spot_name': 'Chitwan National Park',
                'rating': 5,
                'comment': 'Amazing wildlife experience! Saw rhinos, deer, and many birds. The jungle walk was thrilling.',
                'visit_date': date(2024, 12, 5)
            },
            {
                'user_username': 'sita_explorer',
                'spot_name': 'Kathmandu Valley Viewpoint',
                'rating': 3,
                'comment': 'Good views but road construction makes it difficult to reach. Better to visit after construction is completed.',
                'visit_date': date(2024, 11, 1)
            }
        ]

        print("Creating sample reviews...")
        for review_data in reviews_data:
            user = User.query.filter_by(username=review_data['user_username']).first()
            spot = NatureSpot.query.filter_by(name=review_data['spot_name']).first()
            
            if user and spot:
                existing_review = Review.query.filter_by(user_id=user.id, nature_spot_id=spot.id).first()
                if not existing_review:
                    review = Review(
                        user_id=user.id,
                        nature_spot_id=spot.id,
                        rating=review_data['rating'],
                        comment=review_data['comment'],
                        visit_date=review_data['visit_date']
                    )
                    db.session.add(review)

        # Create sample community tips
        tips_data = [
            {
                'user_username': 'bikash_trekker',
                'spot_name': 'Nagarkot Sunrise Point',
                'tip_type': 'season',
                'content': 'Best time is during winter months for clear mountain views. Arrive by 5:30 AM for sunrise.'
            },
            {
                'user_username': 'sita_explorer',
                'spot_name': 'Phewa Lake',
                'tip_type': 'transport',
                'content': 'Take a taxi from Pokhara city center. Boats are available for rent near Barahi Temple.'
            },
            {
                'user_username': 'ramesh_hiker',
                'spot_name': 'Sekumpana Waterfall',
                'tip_type': 'packing',
                'content': 'Bring waterproof gear and sturdy hiking boots. The trail can be muddy during monsoon.'
            },
            {
                'user_username': 'bikash_trekker',
                'spot_name': 'Chitwan National Park',
                'tip_type': 'safety',
                'content': 'Always stay with your guide and follow park rules. Wear neutral colored clothing for wildlife viewing.'
            }
        ]

        print("Creating sample community tips...")
        for tip_data in tips_data:
            user = User.query.filter_by(username=tip_data['user_username']).first()
            spot = NatureSpot.query.filter_by(name=tip_data['spot_name']).first()
            
            if user and spot:
                tip = CommunityTip(
                    user_id=user.id,
                    nature_spot_id=spot.id,
                    tip_type=tip_data['tip_type'],
                    content=tip_data['content']
                )
                db.session.add(tip)

        # Create some sample visits and bookmarks
        print("Creating sample visits and bookmarks...")
        for user in users:
            if not user.is_admin:
                # Add some random visits
                for spot in random.sample(spots, min(3, len(spots))):
                    existing_visit = Visit.query.filter_by(user_id=user.id, nature_spot_id=spot.id).first()
                    if not existing_visit:
                        visit = Visit(
                            user_id=user.id,
                            nature_spot_id=spot.id,
                            visit_date=date(2024, random.randint(8, 12), random.randint(1, 28))
                        )
                        db.session.add(visit)
                
                # Add some random bookmarks
                for spot in random.sample(spots, min(2, len(spots))):
                    existing_bookmark = Bookmark.query.filter_by(user_id=user.id, nature_spot_id=spot.id).first()
                    if not existing_bookmark:
                        bookmark = Bookmark(
                            user_id=user.id,
                            nature_spot_id=spot.id
                        )
                        db.session.add(bookmark)

        db.session.commit()
        print("Sample data created successfully!")
        print("\nLogin credentials:")
        print("Admin: username='admin', password='admin123'")
        print("User 1: username='ramesh_hiker', password='password123'")
        print("User 2: username='sita_explorer', password='password123'")
        print("User 3: username='bikash_trekker', password='password123'")

if __name__ == "__main__":
    create_sample_data()