"""
Sample data creation utilities for ConsultEase development and testing.
"""

import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

def create_sample_faculty_data(faculty_controller) -> bool:
    """
    Create sample faculty data using the faculty controller.
    
    Args:
        faculty_controller: The FacultyController instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        # Sample faculty data with diverse statuses
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
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for faculty_data in sample_faculty:
            try:
                # Check if faculty already exists
                existing_faculty = faculty_controller.get_faculty_by_email(faculty_data['email'])
                
                if existing_faculty:
                    # Update existing faculty status
                    success = faculty_controller.update_faculty_status(
                        existing_faculty.id, 
                        faculty_data['status']
                    )
                    if success:
                        updated_count += 1
                        logger.info(f"Updated faculty: {faculty_data['name']} - Status: {faculty_data['status']}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to update faculty: {faculty_data['name']}")
                else:
                    # Create new faculty
                    faculty, errors = faculty_controller.add_faculty(
                        name=faculty_data['name'],
                        department=faculty_data['department'],
                        email=faculty_data['email'],
                        ble_id=faculty_data['ble_id'],
                        image_path=None,
                        always_available=False
                    )
                    
                    if faculty and not errors:
                        # Set the initial status after creation
                        faculty_controller.update_faculty_status(faculty.id, faculty_data['status'])
                        created_count += 1
                        logger.info(f"Created faculty: {faculty_data['name']} - {faculty_data['department']}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to create faculty: {faculty_data['name']}, Errors: {errors}")
                        
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing faculty {faculty_data['name']}: {e}")
                continue
        
        # Log summary
        logger.info("=" * 60)
        logger.info("✅ Sample faculty data creation completed!")
        logger.info(f"📊 Created: {created_count} new faculty")
        logger.info(f"📊 Updated: {updated_count} existing faculty")
        if error_count > 0:
            logger.warning(f"⚠️ Errors: {error_count} faculty had issues")
        logger.info("=" * 60)
        
        return error_count == 0
        
    except Exception as e:
        logger.error(f"Error in create_sample_faculty_data: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def get_sample_consultation_data() -> List[Dict]:
    """
    Get sample consultation data for testing.
    
    Returns:
        List[Dict]: Sample consultation data
    """
    return [
        {
            'student_id': 1,
            'faculty_id': 1,
            'message': 'Need help with database design for my capstone project',
            'course_code': 'CS401',
            'status': 'pending'
        },
        {
            'student_id': 1,
            'faculty_id': 2,
            'message': 'Questions about software architecture patterns',
            'course_code': 'SE301',
            'status': 'accepted'
        },
        {
            'student_id': 1,
            'faculty_id': 3,
            'message': 'Help with machine learning algorithms',
            'course_code': 'DS201',
            'status': 'completed'
        }
    ]

def ensure_sample_data_exists(faculty_controller) -> bool:
    """
    Ensure sample data exists in the database for testing/demo purposes.
    
    Args:
        faculty_controller: The FacultyController instance
        
    Returns:
        bool: True if sample data exists or was created successfully
    """
    try:
        # Check if we have enough faculty for a good demo
        all_faculty = faculty_controller.get_all_faculty()
        
        if len(all_faculty) < 5:
            logger.info("Insufficient faculty data for demo, creating sample data...")
            return create_sample_faculty_data(faculty_controller)
        else:
            logger.info(f"Sufficient faculty data exists ({len(all_faculty)} faculty members)")
            return True
            
    except Exception as e:
        logger.error(f"Error checking sample data: {e}")
        return False 