import logging
import datetime
from ..models import Consultation, ConsultationStatus, get_db, Faculty
from ..utils.mqtt_utils import publish_consultation_request, publish_mqtt_message
from ..utils.mqtt_topics import MQTTTopics
from ..utils.cache_manager import invalidate_consultation_cache, invalidate_faculty_cache
from ..services.consultation_queue_service import get_consultation_queue_service, MessagePriority
from sqlalchemy.orm import joinedload
from ..services.async_mqtt_service import get_async_mqtt_service

# Set up logging
logger = logging.getLogger(__name__)

class ConsultationController:
    """
    Controller for managing consultation requests.
    """

    def __init__(self):
        """
        Initialize the consultation controller.
        """
        self.callbacks = []
        self.queue_service = get_consultation_queue_service()

    def start(self):
        """
        Start the consultation controller.
        """
        logger.info("Starting Consultation controller")
        # Start the consultation queue service
        self.queue_service.start()
        # Async MQTT service is managed globally, no need to connect here

    def stop(self):
        """
        Stop the consultation controller.
        """
        logger.info("Stopping Consultation controller")

    def register_callback(self, callback):
        """
        Register a callback to be called when a consultation status changes.

        Args:
            callback (callable): Function that takes a Consultation object as argument
        """
        self.callbacks.append(callback)
        logger.info(f"Registered Consultation controller callback: {callback.__name__}")

    def _notify_callbacks(self, consultation):
        """
        Notify all registered callbacks with the updated consultation information.

        Args:
            consultation (Consultation): Updated consultation object
        """
        for callback in self.callbacks:
            try:
                callback(consultation)
            except Exception as e:
                logger.error(f"Error in Consultation controller callback: {str(e)}")

    def create_consultation(self, student_id, faculty_id, request_message, course_code=None):
        """
        Create a new consultation request.

        Args:
            student_id (int): Student ID
            faculty_id (int): Faculty ID
            request_message (str): Consultation request message
            course_code (str, optional): Course code

        Returns:
            Consultation: New consultation object or None if error
        """
        db = get_db()
        try:
            logger.info(f"Creating new consultation request (Student: {student_id}, Faculty: {faculty_id})")

            # Create new consultation
            consultation = Consultation(
                student_id=student_id,
                faculty_id=faculty_id,
                request_message=request_message,
                course_code=course_code,
                status=ConsultationStatus.PENDING,
                requested_at=datetime.datetime.now()
            )

            db.add(consultation)
            db.commit()

            logger.info(f"Created consultation request: {consultation.id} (Student: {student_id}, Faculty: {faculty_id})")

            # Publish consultation using the optimized method with offline queuing
            publish_success = self._publish_consultation(consultation)

            if publish_success:
                logger.info(f"Successfully published consultation request {consultation.id} to faculty desk unit")
            else:
                # Try to queue the consultation for offline faculty
                queue_success = self.queue_service.queue_consultation_request(consultation, MessagePriority.NORMAL)
                if queue_success:
                    logger.info(f"Queued consultation request {consultation.id} for offline faculty {faculty_id}")
                else:
                    logger.error(f"Failed to publish or queue consultation request {consultation.id}")

            # Invalidate consultation cache for both student and faculty
            try:
                invalidate_consultation_cache(student_id)
                invalidate_consultation_cache(faculty_id)
            except Exception as e:
                logger.warning(f"Failed to invalidate consultation cache: {str(e)}")

            # Notify callbacks
            self._notify_callbacks(consultation)

            return consultation

        except Exception as e:
            logger.error(f"Error creating consultation: {str(e)}")
            db.rollback()
            return None
        finally:
            # ✅ FIXED: Ensure database session is always closed
            db.close()

    def _publish_consultation(self, consultation):
        """
        Publish consultation to MQTT using async service.

        Args:
            consultation (Consultation): Consultation object to publish
        """
        try:
            # Get a new database session and fetch the consultation with all related objects
            db = get_db(force_new=True)

            # Instead of refreshing, query for the consultation by ID to ensure it's attached to this session
            consultation_id = consultation.id
            consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()

            if not consultation:
                logger.error(f"Consultation with ID {consultation_id} not found in database")
                return False

            # Explicitly load the related objects to avoid lazy loading issues
            student = consultation.student
            faculty = consultation.faculty

            if not student:
                logger.error(f"Student not found for consultation {consultation_id}")
                return False

            if not faculty:
                logger.error(f"Faculty not found for consultation {consultation_id}")
                return False

            # Prepare consultation data for async publishing
            consultation_data = {
                'id': consultation.id,
                'student_id': student.id,
                'student_name': student.name,
                'student_department': student.department,
                'faculty_id': faculty.id,
                'faculty_name': faculty.name,
                'request_message': consultation.request_message,
                'course_code': consultation.course_code,
                'status': consultation.status.value,
                'requested_at': consultation.requested_at.isoformat() if consultation.requested_at else None
            }

            logger.info(f"Publishing consultation request {consultation.id} for faculty {faculty.id} using async MQTT")

            # Use the async MQTT utility function
            success = publish_consultation_request(consultation_data)

            # Also publish to legacy topic for backward compatibility
            message = f"Student: {student.name}\n"
            if consultation.course_code:
                message += f"Course: {consultation.course_code}\n"
            message += f"Request: {consultation.request_message}"

            legacy_topic = MQTTTopics.LEGACY_FACULTY_MESSAGES
            legacy_success = publish_mqtt_message(legacy_topic, message, qos=2)

            # Close the database session
            db.close()

            overall_success = success or legacy_success
            if overall_success:
                logger.info(f"Successfully published consultation request {consultation.id} using async MQTT")
            else:
                logger.error(f"Failed to publish consultation request {consultation.id} using async MQTT")

            return overall_success
        except Exception as e:
            logger.error(f"Error publishing consultation: {str(e)}")
            return False

    def _publish_consultation_update(self, faculty_id, consultation_id, action, student_name=None, message_details=None):
        """
        Publish a consultation update (e.g., cancellation) to the faculty desk unit.
        """
        try:
            topic = MQTTTopics.FACULTY_REQUESTS_TOPIC_TEMPLATE.format(faculty_id=faculty_id)
            payload = {
                "action": action,
                "consultation_id": str(consultation_id) # Ensure ID is string for ESP32 JSON parsing
            }
            # For potential future use, if more details are needed for other actions
            if student_name:
                payload["student_name"] = student_name
            if message_details:
                payload["message"] = message_details

            logger.info(f"Publishing consultation update to {topic}: {payload}")
            
            # Directly use the utility that handles async publishing and potential queuing
            # publish_mqtt_message is more generic, let's use a more specific one if available
            # or ensure publish_mqtt_message can handle a dict payload correctly (it should json.dumps it)
            mqtt_service = get_async_mqtt_service()
            
            import json
            mqtt_service.publish(topic, json.dumps(payload), qos=1) # Use QoS 1 for cancellations
            logger.info(f"Successfully published {action} for consultation {consultation_id} to faculty {faculty_id}")
            return True
        except Exception as e:
            logger.error(f"Error publishing consultation update for {consultation_id}: {e}")
            return False

    def update_consultation_status(self, consultation_id, status):
        """
        Update consultation status.

        Args:
            consultation_id (int): Consultation ID
            status (ConsultationStatus): New status

        Returns:
            Consultation: Updated consultation object or None if error
        """
        db = get_db()
        try:
            consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()

            if not consultation:
                logger.error(f"Consultation not found: {consultation_id}")
                return None

            # Store old status for logging
            old_status = consultation.status

            # Update status and timestamp
            consultation.status = status

            if status == ConsultationStatus.ACCEPTED:
                consultation.accepted_at = datetime.datetime.now()
            elif status == ConsultationStatus.BUSY:
                consultation.busy_at = datetime.datetime.now()
            elif status == ConsultationStatus.COMPLETED:
                consultation.completed_at = datetime.datetime.now()
            elif status == ConsultationStatus.CANCELLED:
                # No specific timestamp for cancellation, but we could add one if needed
                pass # Timestamping will be handled in cancel_consultation

            db.commit()

            logger.info(f"✅ Updated consultation status: {consultation.id} ({old_status.value} -> {status.value})")

            # ✅ FIXED: Don't republish consultation as this confuses the faculty desk unit
            # The faculty already responded, no need to send it back to them
            
            # ✅ ENHANCED: Invalidate cache for both student and faculty
            try:
                invalidate_consultation_cache(consultation.student_id)
                invalidate_consultation_cache(consultation.faculty_id)
                logger.debug(f"Invalidated consultation cache for student {consultation.student_id} and faculty {consultation.faculty_id}")
            except Exception as e:
                logger.warning(f"Failed to invalidate consultation cache: {str(e)}")

            # Notify callbacks with the updated consultation
            self._notify_callbacks(consultation)

            return consultation

        except Exception as e:
            logger.error(f"Error updating consultation status: {str(e)}")
            db.rollback()
            return None
        finally:
            # ✅ CRITICAL FIX: Always close the database session
            db.close()

    def cancel_consultation(self, consultation_id: int):
        """
        Cancel a consultation request.
        Updates status to CANCELLED, sets timestamp, and notifies faculty unit via MQTT.
        """
        db = get_db()
        try:
            logger.info(f"Attempting to cancel consultation ID: {consultation_id}")
            consultation = db.query(Consultation).options(joinedload(Consultation.faculty)).filter(Consultation.id == consultation_id).first()

            if not consultation:
                logger.error(f"Consultation not found for cancellation: {consultation_id}")
                return None

            if consultation.status == ConsultationStatus.CANCELLED:
                logger.warning(f"Consultation {consultation_id} is already cancelled.")
                # Optionally return the consultation object if needed by caller
                return consultation
            
            if consultation.status not in [ConsultationStatus.PENDING, ConsultationStatus.ACCEPTED]:
                logger.warning(f"Consultation {consultation_id} cannot be cancelled. Status: {consultation.status.value}")
                # Depending on requirements, this might raise an error or return a specific status
                return None # Or raise an exception like ValueError("Consultation cannot be cancelled")

            consultation.status = ConsultationStatus.CANCELLED
            consultation.cancelled_at = datetime.datetime.now() # Add a timestamp for cancellation
            consultation.updated_at = datetime.datetime.now()

            db.commit()
            logger.info(f"Consultation {consultation_id} status updated to CANCELLED in DB.")

            # Publish cancellation to faculty desk unit
            if consultation.faculty:
                self._publish_consultation_update(
                    faculty_id=consultation.faculty.id,
                    consultation_id=consultation.id,
                    action="CANCEL_CONSULTATION"
                )
            else:
                logger.warning(f"Faculty information not available for consultation {consultation_id}. Cannot send MQTT cancellation.")


            # Invalidate caches
            try:
                invalidate_consultation_cache(consultation.student_id)
                if consultation.faculty_id:
                    invalidate_consultation_cache(consultation.faculty_id) # Faculty might also have a cache view
                    invalidate_faculty_cache(consultation.faculty_id)
                logger.debug(f"Invalidated caches for consultation {consultation_id}")
            except Exception as e:
                logger.warning(f"Failed to invalidate cache during cancellation: {str(e)}")

            # Notify callbacks (e.g., UI refresh)
            self._notify_callbacks(consultation)
            logger.info(f"Successfully cancelled consultation {consultation_id}")
            return consultation

        except Exception as e:
            logger.error(f"Error cancelling consultation {consultation_id}: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()

    def get_consultations(self, student_id=None, faculty_id=None, status=None):
        """
        Get consultations from the database with various filters.
        Enhanced to load related faculty and student data to prevent lazy loading issues.
        """
        db = get_db()
        try:
            query = db.query(Consultation).options(
                joinedload(Consultation.student),
                joinedload(Consultation.faculty)
            )

            if student_id:
                query = query.filter(Consultation.student_id == student_id)
            if faculty_id:
                query = query.filter(Consultation.faculty_id == faculty_id)
            if status:
                if isinstance(status, list):
                    query = query.filter(Consultation.status.in_(status))
                else:
                    query = query.filter(Consultation.status == status)
            
            # Order by most recent first
            consultations = query.order_by(Consultation.requested_at.desc()).all()
            
            # Log consultation details if any found
            if consultations:
                logger.debug(f"Retrieved {len(consultations)} consultations with filters (student: {student_id}, faculty: {faculty_id}, status: {status})")
                # for c in consultations:
                #     logger.debug(f"  - ID: {c.id}, Status: {c.status.value}, Student: {c.student.name if c.student else 'N/A'}, Faculty: {c.faculty.name if c.faculty else 'N/A'}")
            else:
                logger.debug(f"No consultations found with filters (student: {student_id}, faculty: {faculty_id}, status: {status})")
                
            return consultations
        except Exception as e:
            logger.error(f"Error getting consultations: {str(e)}")
            return []
        finally:
            db.close()

    def get_consultation_by_id(self, consultation_id: int):
        """
        Get a single consultation by ID with related student and faculty data.
        """
        db = get_db()
        try:
            consultation = db.query(Consultation).options(
                joinedload(Consultation.student),
                joinedload(Consultation.faculty)
            ).filter(Consultation.id == consultation_id).first()
            
            if consultation:
                logger.debug(f"Retrieved consultation ID {consultation_id}: Status {consultation.status.value}")
            else:
                logger.warning(f"Consultation ID {consultation_id} not found.")
                
            return consultation
        except Exception as e:
            logger.error(f"Error getting consultation by ID {consultation_id}: {str(e)}")
            return None
        finally:
            db.close()

    def test_faculty_desk_connection(self, faculty_id: int):
        """
        Test the connection to a faculty desk unit by sending a test message.

        Args:
            faculty_id (int): Faculty ID to test

        Returns:
            bool: True if the test message was sent successfully, False otherwise
        """
        try:
            # Get faculty information
            db = get_db()
            faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()

            if not faculty:
                logger.error(f"Faculty not found: {faculty_id}")
                return False

            # Create a test message
            message = f"Test message from ConsultEase central system.\nTimestamp: {datetime.datetime.now().isoformat()}"

            # Publish to faculty-specific topic using standardized format
            faculty_requests_topic = MQTTTopics.get_faculty_requests_topic(faculty_id)
            payload = {
                'id': 0,
                'student_id': 0,
                'student_name': "System Test",
                'student_department': "System",
                'faculty_id': faculty_id,
                'faculty_name': faculty.name,
                'request_message': message,
                'course_code': "TEST",
                'status': "test",
                'requested_at': datetime.datetime.now().isoformat(),
                'message': message
            }

            # Publish using async MQTT service
            success_json = publish_mqtt_message(faculty_requests_topic, payload)

            # Publish to legacy plain text topic for backward compatibility
            success_text = publish_mqtt_message(MQTTTopics.LEGACY_FACULTY_MESSAGES, message, qos=2)

            # Publish to faculty-specific plain text topic
            faculty_messages_topic = MQTTTopics.get_faculty_messages_topic(faculty_id)
            success_faculty = publish_mqtt_message(faculty_messages_topic, message, qos=2)

            logger.info(f"Test message sent to faculty desk unit {faculty_id} ({faculty.name}) using async MQTT")
            logger.info(f"JSON topic success: {success_json}, Text topic success: {success_text}, Faculty topic success: {success_faculty}")

            return success_json or success_text or success_faculty
        except Exception as e:
            logger.error(f"Error testing faculty desk connection: {str(e)}")
            return False