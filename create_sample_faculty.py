#!/usr/bin/env python3
"""
Script to create sample faculty data for ConsultEase development and testing.
Run this script to populate the database with sample faculty members.
"""

import sys
import os
import logging
from datetime import datetime

# Add the central_system directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'central_system'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_faculty():
    """Create sample faculty data for testing and development."""
    
    try:
        from central_system.models import init_db, get_db, Faculty
        
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Sample faculty data
        sample_faculty = [
            {
                'name': 'Dr. Maria Santos',
                'department': 'Computer Science',
                'email': 'maria.santos@consultease.edu',
                'ble_id': 'BLE001',
                'status': True  # Available
            },
            {
                'name': 'Prof. John Rodriguez',
                'department': 'Information Technology',
                'email': 'john.rodriguez@consultease.edu', 
                'ble_id': 'BLE002',
                'status': False  # Unavailable
            },
            {
                'name': 'Dr. Sarah Chen',
                'department': 'Software Engineering',
                'email': 'sarah.chen@consultease.edu',
                'ble_id': 'BLE003',
                'status': True  # Available
            },
            {
                'name': 'Prof. Michael Thompson',
                'department': 'Computer Science',
                'email': 'michael.thompson@consultease.edu',
                'ble_id': 'BLE004',
                'status': False  # Unavailable
            },
            {
                'name': 'Dr. Jennifer Lee',
                'department': 'Data Science',
                'email': 'jennifer.lee@consultease.edu',
                'ble_id': 'BLE005',
                'status': True  # Available
            },
            {
                'name': 'Prof. David Wilson',
                'department': 'Information Systems',
                'email': 'david.wilson@consultease.edu',
                'ble_id': 'BLE006',
                'status': False  # Unavailable
            },
            {
                'name': 'Dr. Emily Garcia',
                'department': 'Computer Engineering',
                'email': 'emily.garcia@consultease.edu',
                'ble_id': 'BLE007',
                'status': True  # Available
            },
            {
                'name': 'Prof. Robert Kim',
                'department': 'Network Security',
                'email': 'robert.kim@consultease.edu',
                'ble_id': 'BLE008',
                'status': False  # Unavailable
            }
        ]
        
        db = get_db()
        
        created_count = 0
        updated_count = 0
        
        for faculty_data in sample_faculty:
            try:
                # Check if faculty already exists by email
                existing = db.query(Faculty).filter(Faculty.email == faculty_data['email']).first()
                
                if existing:
                    logger.info(f"Faculty {faculty_data['name']} already exists, updating status...")
                    existing.status = faculty_data['status']
                    existing.department = faculty_data['department']
                    existing.ble_id = faculty_data['ble_id']
                    updated_count += 1
                else:
                    # Create new faculty
                    faculty = Faculty(
                        name=faculty_data['name'],
                        department=faculty_data['department'],
                        email=faculty_data['email'],
                        ble_id=faculty_data['ble_id'],
                        status=faculty_data['status'],
                        always_available=False,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    db.add(faculty)
                    created_count += 1
                    logger.info(f"Created faculty: {faculty_data['name']} - {faculty_data['department']}")
                    
            except Exception as e:
                logger.error(f"Error creating faculty {faculty_data['name']}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        
        # Summary
        total_faculty = db.query(Faculty).count()
        available_faculty = db.query(Faculty).filter(Faculty.status == True).count()
        
        logger.info("=" * 60)
        logger.info("✅ Sample faculty data creation completed!")
        logger.info(f"📊 Created: {created_count} new faculty")
        logger.info(f"📊 Updated: {updated_count} existing faculty")
        logger.info(f"📊 Total faculty in database: {total_faculty}")
        logger.info(f"📊 Available faculty: {available_faculty}")
        logger.info("=" * 60)
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample faculty data: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting sample faculty data creation...")
    success = create_sample_faculty()
    
    if success:
        logger.info("✅ Sample faculty data creation completed successfully!")
        print("\n✅ Sample faculty data has been created!")
        print("🔄 Restart the ConsultEase application to see the new faculty members.")
    else:
        logger.error("❌ Sample faculty data creation failed!")
        print("\n❌ Failed to create sample faculty data. Check the logs for details.")
        sys.exit(1) 