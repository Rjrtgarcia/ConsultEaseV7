"""
Consultation panel module.
Contains the consultation request form and consultation history panel.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QLineEdit, QTextEdit,
                            QComboBox, QMessageBox, QTabWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                            QSizePolicy, QProgressBar, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint, pyqtSlot
from PyQt5.QtGui import QColor

from ..models import ConsultationStatus # Import ConsultationStatus

# Set up logging
logger = logging.getLogger(__name__)

class ConsultationRequestForm(QFrame):
    """
    Form to request a consultation with a faculty member.
    """
    request_submitted = pyqtSignal(object, str, str)

    def __init__(self, faculty=None, parent=None):
        super().__init__(parent)
        self.faculty = faculty
        self.faculty_options = []
        self.init_ui()

    def init_ui(self):
        """
        Initialize the consultation request form UI.
        """
        # Import theme system
        from ..utils.theme import ConsultEaseTheme

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("consultation_request_form")

        # Apply theme-based stylesheet with gold and blue theme
        self.setStyleSheet('''
            QFrame#consultation_request_form {
                background-color: #ffffff;
                border: 2px solid #DAA520;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 16pt;
                color: #1E90FF;
                font-weight: 500;
                margin-bottom: 5px;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #4169E1;
                border-radius: 5px;
                padding: 15px;
                background-color: #ffffff;
                font-size: 16pt;
                color: #333333;
                margin: 5px 0;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #FFD700;
                background-color: #FFFEF7;
            }
            QPushButton {
                border-radius: 5px;
                padding: 15px 25px;
                font-size: 16pt;
                font-weight: bold;
                color: white;
                margin: 10px 0;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        ''')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Form title
        title_label = QLabel("Request Consultation")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #DAA520;")
        main_layout.addWidget(title_label)

        # Faculty selection
        faculty_layout = QHBoxLayout()
        faculty_label = QLabel("Faculty:")
        faculty_label.setFixedWidth(120)
        faculty_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #1E90FF;")
        self.faculty_combo = QComboBox()
        self.faculty_combo.setMinimumWidth(300)
        self.faculty_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #4169E1;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
                font-size: 12pt;
                color: #333333;
            }
            QComboBox:focus {
                border: 2px solid #FFD700;
                background-color: #FFFEF7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #4169E1;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #4169E1;
                selection-background-color: #FFD700;
                selection-color: #333333;
                background-color: #ffffff;
                font-size: 12pt;
            }
        """)
        faculty_layout.addWidget(faculty_label)
        faculty_layout.addWidget(self.faculty_combo)
        main_layout.addLayout(faculty_layout)

        # Course code input
        course_layout = QHBoxLayout()
        course_label = QLabel("Course Code:")
        course_label.setFixedWidth(120)
        course_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #1E90FF;")
        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("e.g., CS101 (optional)")
        self.course_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #4169E1;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
                font-size: 12pt;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
                background-color: #FFFEF7;
            }
        """)
        course_layout.addWidget(course_label)
        course_layout.addWidget(self.course_input)
        main_layout.addLayout(course_layout)

        # Message input
        message_layout = QVBoxLayout()
        message_label = QLabel("Consultation Details:")
        message_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #1E90FF;")
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Describe what you'd like to discuss...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #4169E1;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
                font-size: 12pt;
                color: #333333;
            }
            QTextEdit:focus {
                border: 2px solid #FFD700;
                background-color: #FFFEF7;
            }
        """)
        self.message_input.setMinimumHeight(150)
        message_layout.addWidget(message_label)
        message_layout.addWidget(self.message_input)
        main_layout.addLayout(message_layout)

        # Character count with visual indicator
        char_count_frame = QFrame()
        char_count_layout = QVBoxLayout(char_count_frame)
        char_count_layout.setContentsMargins(0, 0, 0, 0)
        char_count_layout.setSpacing(2)

        # Label and progress bar in a horizontal layout
        count_indicator_layout = QHBoxLayout()
        count_indicator_layout.setContentsMargins(0, 0, 0, 0)

        self.char_count_label = QLabel("0/500 characters")
        self.char_count_label.setAlignment(Qt.AlignLeft)
        self.char_count_label.setStyleSheet("color: #1E90FF; font-size: 11pt; font-weight: bold;")

        # Add a small info label about the limit
        char_limit_info = QLabel("(500 character limit)")
        char_limit_info.setStyleSheet("color: #DAA520; font-size: 10pt; font-weight: bold;")
        char_limit_info.setAlignment(Qt.AlignRight)

        count_indicator_layout.addWidget(self.char_count_label)
        count_indicator_layout.addStretch()
        count_indicator_layout.addWidget(char_limit_info)

        char_count_layout.addLayout(count_indicator_layout)

        # Add progress bar for visual feedback
        self.char_count_progress = QProgressBar()
        self.char_count_progress.setRange(0, 500)
        self.char_count_progress.setValue(0)
        self.char_count_progress.setTextVisible(False)
        self.char_count_progress.setFixedHeight(10)
        self.char_count_progress.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;
                border: 1px solid #DAA520;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #4169E1;
                border-radius: 5px;
            }
        """)

        char_count_layout.addWidget(self.char_count_progress)
        main_layout.addWidget(char_count_frame)

        # Connect text changed signal to update character count
        self.message_input.textChanged.connect(self.update_char_count)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet('''
            QPushButton {
                background-color: #DAA520;
                min-width: 120px;
            }
        ''')
        cancel_button.clicked.connect(self.cancel_request)

        submit_button = QPushButton("Submit Request")
        submit_button.setStyleSheet('''
            QPushButton {
                background-color: #4169E1;
                min-width: 120px;
            }
        ''')
        submit_button.clicked.connect(self.submit_request)

        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(submit_button)

        main_layout.addLayout(button_layout)

    def update_char_count(self):
        """
        Update the character count label and progress bar.
        """
        count = len(self.message_input.toPlainText())
        color = "#1E90FF"  # Default blue
        progress_color = "#4169E1"  # Default blue

        if count > 400:
            color = "#DAA520"  # Warning gold
            progress_color = "#DAA520"
        if count > 500:
            color = "#FF6347"  # Error red-orange
            progress_color = "#FF6347"

        self.char_count_label.setText(f"{count}/500 characters")
        self.char_count_label.setStyleSheet(f"color: {color}; font-size: 11pt; font-weight: bold;")

        # Update progress bar
        self.char_count_progress.setValue(count)
        self.char_count_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #f0f0f0;
                border: 1px solid #DAA520;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {progress_color};
                border-radius: 5px;
            }}
        """)

    def set_faculty(self, faculty):
        """
        Set the faculty for the consultation request.
        Fixed to prevent jarring tab shifting.
        """
        self.faculty = faculty

        # Update the combo box
        if self.faculty and self.faculty_combo.count() > 0:
            for i in range(self.faculty_combo.count()):
                faculty_id = self.faculty_combo.itemData(i)
                if faculty_id == self.faculty.id:
                    self.faculty_combo.setCurrentIndex(i)
                    break

    def set_faculty_options(self, faculty_list):
        """
        Set the available faculty options in the dropdown.
        """
        self.faculty_options = faculty_list
        self.faculty_combo.clear()

        for faculty in faculty_list:
            self.faculty_combo.addItem(f"{faculty.name} ({faculty.department})", faculty.id)

        # If we have a selected faculty, select it in the dropdown
        if self.faculty:
            for i in range(self.faculty_combo.count()):
                faculty_id = self.faculty_combo.itemData(i)
                if faculty_id == self.faculty.id:
                    self.faculty_combo.setCurrentIndex(i)
                    break

    def get_selected_faculty(self):
        """
        Get the selected faculty from the dropdown.
        """
        if self.faculty_combo.count() == 0:
            return self.faculty

        faculty_id = self.faculty_combo.currentData()

        for faculty in self.faculty_options:
            if faculty.id == faculty_id:
                return faculty

        return None

    def submit_request(self):
        """
        Handle the submission of the consultation request with enhanced validation.
        """
        # Validate faculty selection
        faculty = self.get_selected_faculty()
        if not faculty:
            self.show_validation_error("Faculty Selection", "Please select a faculty member.")
            self.faculty_combo.setFocus()
            return

        # Check if faculty is available
        if hasattr(faculty, 'status') and not faculty.status:
            self.show_validation_error("Faculty Availability",
                f"Faculty {faculty.name} is currently unavailable. Please select an available faculty member.")
            self.faculty_combo.setFocus()
            return

        # Validate message content
        message = self.message_input.toPlainText().strip()
        if not message:
            self.show_validation_error("Consultation Details", "Please enter consultation details.")
            self.message_input.setFocus()
            return

        # Check message length
        if len(message) > 500:
            self.show_validation_error("Message Length",
                "Consultation details are too long. Please limit to 500 characters.")
            self.message_input.setFocus()
            return

        # Check message minimum length for meaningful content
        if len(message) < 10:
            self.show_validation_error("Message Content",
                "Please provide more details about your consultation request (minimum 10 characters).")
            self.message_input.setFocus()
            return

        # Validate course code format if provided
        course_code = self.course_input.text().strip()
        if course_code and not self.is_valid_course_code(course_code):
            self.show_validation_error("Course Code Format",
                "Please enter a valid course code (e.g., CS101, MATH202).")
            self.course_input.setFocus()
            return

        # All validation passed, emit signal with the request details
        self.request_submitted.emit(faculty, message, course_code)

    def show_validation_error(self, title, message):
        """
        Show a validation error message using the standardized notification system.

        Args:
            title (str): Error title
            message (str): Error message
        """
        try:
            # Try to use the notification manager
            from ..utils.notification import NotificationManager
            NotificationManager.show_message(
                self,
                title,
                message,
                NotificationManager.WARNING
            )
        except ImportError:
            # Fallback to basic implementation
            error_dialog = QMessageBox(self)
            error_dialog.setWindowTitle("Validation Error")
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.setText(f"<b>{title}</b>")
            error_dialog.setInformativeText(message)
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.setDefaultButton(QMessageBox.Ok)
            error_dialog.setStyleSheet("""
                QMessageBox {
                    background-color: #f8f9fa;
                }
                QLabel {
                    color: #212529;
                    font-size: 12pt;
                }
                QPushButton {
                    background-color: #0d3b66;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #0a2f52;
                }
            """)
            error_dialog.exec_()

    def is_valid_course_code(self, course_code):
        """
        Validate course code format.

        Args:
            course_code (str): Course code to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation: 2-4 letters followed by 3-4 numbers, optionally followed by a letter
        import re
        pattern = r'^[A-Za-z]{2,4}\d{3,4}[A-Za-z]?$'

        # Allow common formats like CS101, MATH202, ENG101A
        return bool(re.match(pattern, course_code))

    def cancel_request(self):
        """
        Cancel the consultation request.
        """
        self.message_input.clear()
        self.course_input.clear()
        self.setVisible(False)

class ConsultationHistoryPanel(QFrame):
    """
    Panel to display consultation history.
    """
    consultation_selected = pyqtSignal(object)
    consultation_cancelled = pyqtSignal(int)

    def __init__(self, student=None, parent=None):
        super().__init__(parent)
        self.student = student
        self.consultations = []
        self.mqtt_client = None
        self.init_ui()
        self.setup_mqtt_monitoring()

    def init_ui(self):
        """
        Initialize the consultation history panel UI.
        """
        # Import theme system
        from ..utils.theme import ConsultEaseTheme

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("consultation_history_panel")

        # Apply theme-based stylesheet with gold and blue theme
        self.setStyleSheet('''
            QFrame#consultation_history_panel {
                background-color: #ffffff;
                border: 2px solid #DAA520;
                border-radius: 10px;
                padding: 20px;
            }
            QTableWidget {
                border: 2px solid #4169E1;
                border-radius: 5px;
                background-color: #ffffff;
                alternate-background-color: #FAFAFA;
                gridline-color: #DAA520;
                font-size: 16pt;
                color: #333333;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #DAA520;
            }
            QHeaderView::section {
                background-color: #4169E1;
                color: white;
                padding: 15px;
                border: none;
                font-size: 16pt;
                font-weight: bold;
            }
            QHeaderView::section:first {
                border-top-left-radius: 5px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 5px;
            }
            /* Improve scrollbar visibility */
            QScrollBar:vertical {
                background: #FAFAFA;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #DAA520;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #B8860B;
            }
            QPushButton {
                border-radius: 5px;
                padding: 12px 20px;
                font-size: 15pt;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        ''')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("My Consultation History")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #DAA520;")
        main_layout.addWidget(title_label)

        # Consultation table
        self.consultation_table = QTableWidget()
        self.consultation_table.setColumnCount(5)
        self.consultation_table.setHorizontalHeaderLabels(["Faculty", "Course", "Status", "Date", "Actions"])

        # Improved column sizing to ensure action buttons are fully visible
        header = self.consultation_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Faculty - stretch to fill
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Course - fit content
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Status - fit content
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Date - fit content
        header.setSectionResizeMode(4, QHeaderView.Fixed) # Actions - fixed width
        
        # Set minimum widths for better button visibility
        header.setMinimumSectionSize(100)  # Minimum width for any column
        self.consultation_table.setColumnWidth(4, 180)  # Fixed width for Actions column to ensure buttons fit
        
        # Set minimum row height to accommodate buttons properly
        self.consultation_table.verticalHeader().setDefaultSectionSize(50)  # Increase row height
        self.consultation_table.verticalHeader().setMinimumSectionSize(45)  # Minimum row height

        self.consultation_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.consultation_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.consultation_table.setSelectionMode(QTableWidget.SingleSelection)
        self.consultation_table.setAlternatingRowColors(True)

        main_layout.addWidget(self.consultation_table)

        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet('''
            QPushButton {
                background-color: #4169E1;
                min-width: 120px;
            }
        ''')
        refresh_button.clicked.connect(self.refresh_consultations)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)

        main_layout.addLayout(button_layout)

    def set_student(self, student):
        """
        Set the student for the consultation history.
        """
        self.student = student
        self.refresh_consultations()

    def refresh_consultations(self):
        """
        Refresh the consultation list from the database.
        """
        if not self.student:
            logger.warning("Cannot refresh consultations - no student set")
            return

        # Add debug logging
        student_id = self.student.get('id') if isinstance(self.student, dict) else getattr(self.student, 'id', None)
        logger.info(f"🔄 REFRESHING CONSULTATIONS for student {student_id}")

        # Clear existing consultations
        self.consultations.clear()

        # Show loading state
        self.consultation_table.setRowCount(0)
        self.consultation_table.setItem(0, 0, QTableWidgetItem("Loading consultations..."))
        
        try:
            # Import consultation controller
            from ..controllers.consultation_controller import ConsultationController
            consultation_controller = ConsultationController()

            # Get consultations for the current student using the correct method
            consultations = consultation_controller.get_consultations(student_id=student_id)
            logger.info(f"📊 CONSULTATION REFRESH - Found {len(consultations)} consultations for student {student_id}")
            
            # Log details of each consultation
            for i, consultation in enumerate(consultations):
                logger.debug(f"   Consultation {i+1}: ID={consultation.id}, Status={consultation.status.value}, Faculty={consultation.faculty_id}, Created={consultation.created_at}")
            
            # Update consultations and table
            logger.info(f"✅ CONSULTATION LOAD SUCCESS - Processing {len(consultations)} consultations")
            self.consultations = consultations
            self.update_consultation_table()
            logger.info(f"✅ CONSULTATION TABLE UPDATED with {len(consultations)} rows")
            
        except Exception as e:
            logger.error(f"❌ CONSULTATION REFRESH ERROR: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            # Show error state in table
            self.consultation_table.setRowCount(1)
            self.consultation_table.setItem(0, 0, QTableWidgetItem("Error loading consultations"))

    def update_consultation_table(self):
        """
        Update the consultation table with the current consultations.
        """
        # Clear the table
        self.consultation_table.setRowCount(0)

        # Add consultations to the table
        for consultation in self.consultations:
            row_position = self.consultation_table.rowCount()
            self.consultation_table.insertRow(row_position)

            # Faculty name
            faculty_name = consultation.faculty.name if hasattr(consultation, 'faculty') and consultation.faculty else "N/A"
            faculty_item = QTableWidgetItem(faculty_name)
            self.consultation_table.setItem(row_position, 0, faculty_item)

            # Course code
            course_item = QTableWidgetItem(consultation.course_code if consultation.course_code else "N/A")
            self.consultation_table.setItem(row_position, 1, course_item)

            # Status with enhanced color coding and improved contrast
            status_item = QTableWidgetItem(consultation.status.value.capitalize())

            # Define status colors with gold and blue theme
            status_colors = {
                "pending": {
                    "bg": QColor(255, 248, 220),  # Light goldenrod background
                    "fg": QColor(184, 134, 11),   # Dark goldenrod text
                    "border": "#DAA520"           # Goldenrod border
                },
                "accepted": {
                    "bg": QColor(240, 248, 255),  # Very light blue background
                    "fg": QColor(34, 139, 34),    # Forest green text
                    "border": "#228B22"           # Green border for accepted
                },
                "busy": {
                    "bg": QColor(255, 245, 245),  # Very light red background  
                    "fg": QColor(220, 53, 69),    # Red text
                    "border": "#dc3545"           # Red border
                },
                "completed": {
                    "bg": QColor(230, 240, 255),  # Light blue background
                    "fg": QColor(65, 105, 225),   # Royal blue text
                    "border": "#4169E1"           # Royal blue border
                },
                "cancelled": {
                    "bg": QColor(255, 245, 245),  # Light red background
                    "fg": QColor(178, 134, 11),   # Dark goldenrod text
                    "border": "#B8860B"           # Dark goldenrod border
                }
            }

            # Apply the appropriate color scheme
            status_value = consultation.status.value
            if status_value in status_colors:
                colors = status_colors[status_value]
                status_item.setBackground(colors["bg"])
                status_item.setForeground(colors["fg"])

                # Apply custom styling with border for better definition
                status_item.setData(
                    Qt.UserRole,
                    f"border: 2px solid {colors['border']}; border-radius: 4px; padding: 4px;"
                )

            # Make text bold and slightly larger for better readability
            font = status_item.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() + 1)
            status_item.setFont(font)
            self.consultation_table.setItem(row_position, 2, status_item)

            # Date
            date_str = consultation.requested_at.strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_str)
            self.consultation_table.setItem(row_position, 3, date_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0) # Reduced margins
            actions_layout.setSpacing(5) # Reduced spacing

            # View Details Button (example)
            # view_button = QPushButton("View")
            # view_button.setStyleSheet("background-color: #17a2b8; font-size: 11pt; padding: 5px;") # Smaller padding
            # view_button.clicked.connect(lambda _, c=consultation: self.view_consultation_details(c))
            # actions_layout.addWidget(view_button)

            # Cancel Button - only if status is PENDING or ACCEPTED
            if consultation.status in [ConsultationStatus.PENDING, ConsultationStatus.ACCEPTED]:
                cancel_button = QPushButton("Cancel")
                cancel_button.setStyleSheet("background-color: #dc3545; font-size: 11pt; padding: 5px;") # Smaller padding
                # Use a lambda to pass the specific consultation object to the handler
                cancel_button.clicked.connect(lambda checked, c=consultation: self.cancel_consultation(c))
                actions_layout.addWidget(cancel_button)
            else:
                # Add a placeholder or an empty stretch if no actions applicable for this row, to keep alignment
                actions_layout.addStretch()

            actions_layout.addStretch() # Ensure buttons are to the left
            self.consultation_table.setCellWidget(row_position, 4, actions_widget)

            # Set row height for better visuals with buttons
            self.consultation_table.setRowHeight(row_position, 55) # Adjusted row height

        self.consultation_table.resizeRowsToContents()

    def view_consultation_details(self, consultation):
        """
        Show consultation details in a dialog.
        """
        dialog = ConsultationDetailsDialog(consultation, self)
        dialog.exec_()

    def cancel_consultation(self, consultation):
        """
        Cancel a pending consultation with improved confirmation dialog.
        """
        try:
            # Try to use the notification manager for confirmation
            from ..utils.notification import NotificationManager

            # Show confirmation dialog
            if NotificationManager.show_confirmation(
                self,
                "Cancel Consultation",
                f"Are you sure you want to cancel your consultation request with {consultation.faculty.name}?",
                "Yes, Cancel",
                "No, Keep It"
            ):
                # Emit signal to cancel the consultation
                self.consultation_cancelled.emit(consultation.id)

        except ImportError:
            # Fallback to basic confirmation dialog
            reply = QMessageBox.question(
                self,
                "Cancel Consultation",
                f"Are you sure you want to cancel your consultation request with {consultation.faculty.name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Emit signal to cancel the consultation
                self.consultation_cancelled.emit(consultation.id)

    def setup_mqtt_monitoring(self):
        """
        Set up MQTT monitoring for faculty responses using the centralized async MQTT service.
        """
        try:
            # Use the centralized async MQTT service instead of creating a separate client
            from ..services.async_mqtt_service import get_async_mqtt_service
            from ..utils.mqtt_utils import subscribe_to_topic
            
            # Get the async MQTT service
            mqtt_service = get_async_mqtt_service()
            
            # Subscribe to faculty response topics using the centralized service
            topics = [
                "consultease/faculty/+/responses",
                "faculty/+/responses",  # Legacy compatibility
                "consultation/+/status",  # Real-time status updates
                "faculty/+/status",  # Faculty availability updates
                "professor/messages",  # Faculty desk unit responses (IMPORTANT!)
            ]
            
            for topic in topics:
                try:
                    # Register topic handler directly with the MQTT service
                    mqtt_service.register_topic_handler(topic, self._handle_mqtt_message_safe)
                    logger.debug(f"Registered MQTT topic handler: {topic}")
                except Exception as e:
                    logger.error(f"Failed to register topic handler {topic}: {e}")
                    
            # Also register with the faculty response controller
            from ..controllers.faculty_response_controller import get_faculty_response_controller
            faculty_controller = get_faculty_response_controller()
            faculty_controller.register_callback(self._handle_faculty_response_callback)
            
            logger.info("MQTT monitoring started for consultation updates using centralized service")
                
        except Exception as e:
            logger.error(f"Failed to setup MQTT monitoring: {e}")

    def _handle_faculty_response_callback(self, response_data):
        """
        Handle faculty response callbacks from the faculty response controller.
        
        Args:
            response_data: Faculty response data including consultation updates
        """
        try:
            # Schedule GUI update in main thread
            QTimer.singleShot(0, lambda: self._process_faculty_callback(response_data))
        except Exception as e:
            logger.error(f"Error handling faculty response callback: {e}")

    def _process_faculty_callback(self, response_data):
        """
        Process faculty response callback in the main thread.
        
        Args:
            response_data: Faculty response data
        """
        try:
            if not self.student:
                return
                
            student_id = self.student.get('id') if isinstance(self.student, dict) else getattr(self.student, 'id', None)
            
            consultation_id = response_data.get('consultation_id') or response_data.get('message_id')
            response_type = response_data.get('response_type', '')
            faculty_name = response_data.get('faculty_name', 'Unknown Faculty')
            callback_student_id = response_data.get('student_id')
            
            logger.info(f"🔄 Processing faculty callback - Student: {student_id}, Consultation: {consultation_id}, Response: {response_type}")
            
            # Check if this response is for the current student
            if callback_student_id and str(callback_student_id) == str(student_id):
                logger.info(f"✅ Faculty response matches current student - showing notification and refreshing")
                
                # Show immediate notification
                self.show_faculty_response_notification(response_type, faculty_name)
                
                # Refresh consultations after a short delay to ensure database is updated
                QTimer.singleShot(1500, self.refresh_consultations)
                
        except Exception as e:
            logger.error(f"Error processing faculty callback: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def _handle_mqtt_message_safe(self, topic: str, data):
        """
        Thread-safe MQTT message handler that schedules GUI updates in the main thread.
        
        Args:
            topic: MQTT topic
            data: Message data
        """
        # Schedule the GUI update in the main thread using QTimer.singleShot
        # This prevents Qt threading violations
        QTimer.singleShot(0, lambda: self._process_mqtt_message(topic, data))

    def _process_mqtt_message(self, topic: str, data):
        """
        Process MQTT messages in the main thread.
        
        Args:
            topic: MQTT topic
            data: Message data
        """
        try:
            import json
            
            # Enhanced logging for debugging
            logger.info(f"🔥 CONSULTATION PANEL - Processing MQTT message:")
            logger.info(f"🔥 Topic: {topic}")
            logger.info(f"🔥 Data Type: {type(data)}")
            logger.info(f"🔥 Raw Data: {data}")
            
            # Parse the message
            if isinstance(data, str):
                message_str = data
                try:
                    response_data = json.loads(message_str)
                    logger.info(f"🔥 Parsed JSON: {response_data}")
                except json.JSONDecodeError:
                    # Handle non-JSON messages
                    response_data = {'raw_message': message_str, 'topic': topic}
                    logger.info(f"🔥 Non-JSON message, created wrapper: {response_data}")
            elif isinstance(data, dict):
                response_data = data
                message_str = json.dumps(data) if data else str(data)
                logger.info(f"🔥 Dict data received: {response_data}")
            else:
                response_data = {'raw_message': str(data), 'topic': topic}
                message_str = str(data)
                logger.info(f"🔥 Unknown data type, created wrapper: {response_data}")
                
            logger.info(f"🔥 Final response_data: {response_data}")
            
            # Process different types of updates
            if 'consultation' in topic.lower() or 'responses' in topic.lower() or 'professor/messages' in topic.lower():
                logger.info(f"🔥 Routing to consultation update handler")
                self._handle_consultation_update(response_data, topic)
            elif 'status' in topic.lower():
                logger.info(f"🔥 Routing to status update handler")
                self._handle_status_update(response_data, topic)
            else:
                logger.info(f"🔥 Unknown topic type, routing to consultation update as fallback")
                self._handle_consultation_update(response_data, topic)
                
        except Exception as e:
            logger.error(f"🔥 Error processing MQTT message: {e}")
            import traceback
            logger.error(f"🔥 Traceback: {traceback.format_exc()}")

    def _handle_consultation_update(self, response_data, topic):
        """
        Handle consultation-specific MQTT updates in the main thread.
        """
        if not self.student:
            return
            
        student_id = self.student.get('id') if isinstance(self.student, dict) else getattr(self.student, 'id', None)
        
        # Extract message details from different possible formats
        message_id = response_data.get('message_id', '') or response_data.get('consultation_id', '')
        response_type = response_data.get('response_type', '')
        faculty_id = response_data.get('faculty_id', '')
        faculty_name = response_data.get('faculty_name', 'Unknown Faculty')
        
        logger.info(f"Processing consultation update - Topic: {topic}, Response Type: {response_type}, Message ID: {message_id}, Faculty ID: {faculty_id}")
        
        # Check if any of our consultations match this response
        consultation_found = False
        
        # Handle different topic formats
        if 'consultease/faculty/' in topic and '/responses' in topic:
            # Extract faculty ID from topic: consultease/faculty/{id}/responses
            try:
                topic_parts = topic.split('/')
                topic_faculty_id = int(topic_parts[2])  # consultease/faculty/{ID}/responses
                
                # Check if this matches any of our consultations
                for consultation in self.consultations:
                    consultation_id_str = str(consultation.id)
                    consultation_faculty_id = getattr(consultation, 'faculty_id', None)
                    
                    # Match by message_id (consultation ID) or by faculty_id for pending consultations
                    if (message_id == consultation_id_str or 
                        (topic_faculty_id == consultation_faculty_id and consultation.status.value == 'pending')):
                        
                        logger.info(f"✅ Found matching consultation {consultation.id} for faculty response")
                        consultation_found = True
                        
                        # Show immediate notification
                        self.show_faculty_response_notification(response_type, faculty_name)
                        break
                        
            except (IndexError, ValueError) as e:
                logger.error(f"Error parsing faculty ID from topic {topic}: {e}")
        
        # Handle legacy professor/messages topic
        elif topic == 'professor/messages':
            # For professor/messages, we need to parse the message content
            # This might contain consultation information
            logger.info("Processing professor/messages topic")
            consultation_found = True  # Assume it's relevant for now
            
            # Show a generic notification
            self.show_faculty_response_notification('UPDATE', 'Faculty')
        
        # Handle other consultation topics
        elif 'consultation' in topic or 'responses' in topic:
            # Generic consultation update
            consultation_found = True
            self.show_faculty_response_notification(response_type or 'UPDATE', faculty_name)
        
        if consultation_found:
            # Schedule refresh after a short delay to allow database update
            QTimer.singleShot(2000, self.refresh_consultations)  # Increased delay to ensure DB is updated
            logger.info(f"Scheduled consultation history refresh due to faculty response")

    def _handle_status_update(self, response_data, topic):
        """
        Handle general status updates (faculty availability, etc.) in the main thread.
        """
        logger.debug(f"Processing status update: {response_data}")
        # Trigger a consultation refresh in case status affects pending consultations
        QTimer.singleShot(500, self.refresh_consultations)

    def show_faculty_response_notification(self, response_type, faculty_name):
        """
        Show notification when faculty responds via desk unit.
        """
        try:
            from ..utils.notification import NotificationManager
            
            if response_type.upper() in ['ACKNOWLEDGE', 'ACCEPTED']:
                title = "Consultation Accepted! ✅"
                message = f"{faculty_name} has accepted your consultation request."
                notification_type = NotificationManager.SUCCESS
            elif response_type.upper() in ['BUSY', 'UNAVAILABLE']:
                title = "Faculty Busy ⏳"
                message = f"{faculty_name} is currently busy and cannot take your consultation."
                notification_type = NotificationManager.WARNING
            else:
                title = "Consultation Update 📬"
                message = f"{faculty_name} has responded to your consultation request."
                notification_type = NotificationManager.INFO
                
            NotificationManager.show_message(
                self,
                title,
                message,
                notification_type
            )
            
        except ImportError:
            # Fallback to basic message box
            QMessageBox.information(
                self,
                "Faculty Response",
                f"{faculty_name} has responded to your consultation request. Please refresh to see the update."
            )

    def __del__(self):
        """
        Cleanup when object is destroyed.
        The MQTT cleanup is now handled by the centralized async MQTT service.
        """
        # No need to cleanup MQTT connection as it's handled by the centralized service
        pass

class ConsultationDetailsDialog(QDialog):
    """
    Dialog to display consultation details.
    """
    def __init__(self, consultation, parent=None):
        super().__init__(parent)
        self.consultation = consultation
        self.init_ui()

    def init_ui(self):
        """
        Initialize the dialog UI.
        """
        # Import theme system
        from ..utils.theme import ConsultEaseTheme

        self.setWindowTitle("Consultation Details")
        self.setMinimumWidth(700)  # Slightly wider for better content display
        self.setMinimumHeight(600)  # Slightly taller for better spacing
        self.setObjectName("consultation_details_dialog")

        # Apply theme-based stylesheet with gold and blue theme
        self.setStyleSheet('''
            QDialog#consultation_details_dialog {
                background-color: #ffffff;
                padding: 15px;
            }
            QLabel {
                font-size: 16pt;
                color: #333333;
                padding: 5px 0;
            }
            QLabel[heading="true"] {
                font-size: 22pt;
                font-weight: bold;
                color: #4169E1;
                margin-bottom: 15px;
                padding: 10px 0;
            }
            QFrame {
                border: 2px solid #DAA520;
                border-radius: 10px;
                background-color: #ffffff;
                padding: 25px;
                margin: 10px 0;
            }
            QPushButton {
                border-radius: 8px;
                padding: 15px 25px;
                font-size: 16pt;
                font-weight: bold;
                color: white;
                background-color: #4169E1;
                min-width: 120px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
            QPushButton:pressed {
                background-color: #0066CC;
            }
        ''')

        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # Increased spacing between elements
        layout.setContentsMargins(20, 20, 20, 20)  # Better margins

        # Title
        title_label = QLabel("Consultation Details")
        title_label.setProperty("heading", "true")
        title_label.setAlignment(Qt.AlignCenter)  # Center the title
        layout.addWidget(title_label)

        # Details frame
        details_frame = QFrame()
        details_layout = QFormLayout(details_frame)
        details_layout.setSpacing(15)  # Increased spacing between form rows
        details_layout.setLabelAlignment(Qt.AlignRight)
        details_layout.setFormAlignment(Qt.AlignLeft)

        # Faculty
        faculty_label = QLabel("Faculty:")
        faculty_label.setStyleSheet("font-weight: bold; color: #DAA520;")
        faculty_value = QLabel(self.consultation.faculty.name)
        faculty_value.setStyleSheet("font-weight: bold; font-size: 17pt; color: #4169E1;")
        details_layout.addRow(faculty_label, faculty_value)

        # Department
        dept_label = QLabel("Department:")
        dept_label.setStyleSheet("font-weight: bold; color: #DAA520;")
        dept_value = QLabel(self.consultation.faculty.department)
        dept_value.setStyleSheet("font-size: 16pt; color: #333333;")
        details_layout.addRow(dept_label, dept_value)

        # Course
        course_label = QLabel("Course:")
        course_label.setStyleSheet("font-weight: bold; color: #DAA520;")
        course_value = QLabel(self.consultation.course_code if self.consultation.course_code else "N/A")
        course_value.setStyleSheet("font-size: 16pt; color: #333333;")
        details_layout.addRow(course_label, course_value)

        # Status with enhanced visual styling
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: bold; color: #DAA520;")
        status_value = QLabel(self.consultation.status.value.capitalize())

        # Define status colors with gold and blue theme
        status_styles = {
            "pending": {
                "color": "#B8860B",                # Dark goldenrod text
                "background": "#FFF8DC",           # Cornsilk background
                "border": "2px solid #DAA520",     # Goldenrod border
                "padding": "10px 15px",
                "border-radius": "8px"
            },
            "accepted": {
                "color": "#228B22",                # Forest green text
                "background": "#f0f8ff",           # Very light blue background
                "border": "2px solid #228B22",     # Green border
                "padding": "10px 15px",
                "border-radius": "8px"
            },
            "busy": {
                "color": "#dc3545",                # Red text
                "background": "#fff5f5",           # Very light red background
                "border": "2px solid #dc3545",     # Red border
                "padding": "10px 15px",
                "border-radius": "8px"
            },
            "completed": {
                "color": "#4169E1",                # Royal blue text
                "background": "#E6F0FF",           # Light blue background
                "border": "2px solid #4169E1",     # Royal blue border
                "padding": "10px 15px",
                "border-radius": "8px"
            },
            "cancelled": {
                "color": "#B8860B",                # Dark goldenrod text
                "background": "#FFF8DC",           # Cornsilk background
                "border": "2px solid #B8860B",     # Dark goldenrod border
                "padding": "10px 15px",
                "border-radius": "8px"
            }
        }

        # Apply the appropriate style
        status_value.setStyleSheet(f"""
            font-weight: bold;
            font-size: 17pt;
            color: {status_styles.get(self.consultation.status.value, {}).get("color", "#212529")};
            background-color: {status_styles.get(self.consultation.status.value, {}).get("background", "#e9ecef")};
            border: {status_styles.get(self.consultation.status.value, {}).get("border", "2px solid #adb5bd")};
            padding: {status_styles.get(self.consultation.status.value, {}).get("padding", "10px 15px")};
            border-radius: {status_styles.get(self.consultation.status.value, {}).get("border-radius", "8px")};
        """)
        details_layout.addRow(status_label, status_value)

        # Requested date
        requested_label = QLabel("Requested:")
        requested_label.setStyleSheet("font-weight: bold; color: #495057;")
        requested_value = QLabel(self.consultation.requested_at.strftime("%Y-%m-%d %H:%M"))
        requested_value.setStyleSheet("font-size: 16pt; color: #343a40;")
        details_layout.addRow(requested_label, requested_value)

        # Accepted date (if applicable)
        if self.consultation.accepted_at:
            accepted_label = QLabel("Accepted:")
            accepted_label.setStyleSheet("font-weight: bold; color: #495057;")
            accepted_value = QLabel(self.consultation.accepted_at.strftime("%Y-%m-%d %H:%M"))
            accepted_value.setStyleSheet("font-size: 16pt; color: #28a745;")
            details_layout.addRow(accepted_label, accepted_value)

        # Busy date (if applicable)
        if self.consultation.busy_at:
            busy_label = QLabel("Marked Busy:")
            busy_label.setStyleSheet("font-weight: bold; color: #495057;")
            busy_value = QLabel(self.consultation.busy_at.strftime("%Y-%m-%d %H:%M"))
            busy_value.setStyleSheet("font-size: 16pt; color: #ffc107;")
            details_layout.addRow(busy_label, busy_value)

        # Completed date (if applicable)
        if self.consultation.completed_at:
            completed_label = QLabel("Completed:")
            completed_label.setStyleSheet("font-weight: bold; color: #495057;")
            completed_value = QLabel(self.consultation.completed_at.strftime("%Y-%m-%d %H:%M"))
            completed_value.setStyleSheet("font-size: 16pt; color: #007bff;")
            details_layout.addRow(completed_label, completed_value)

        layout.addWidget(details_frame)

        # Message section with better spacing
        message_label = QLabel("Consultation Details:")
        message_label.setProperty("heading", "true")
        layout.addWidget(message_label)

        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(20, 20, 20, 20)  # Better padding inside frame

        message_text = QLabel(self.consultation.request_message)
        message_text.setWordWrap(True)
        message_text.setStyleSheet("""
            font-size: 15pt;
            color: #495057;
            padding: 15px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            line-height: 1.5;
        """)
        message_layout.addWidget(message_text)

        layout.addWidget(message_frame)

        # Add some stretch to push the button to the bottom
        layout.addStretch()

        # Close button with better styling and spacing
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)  # Top margin for button separation
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

class ConsultationPanel(QTabWidget):
    """
    Main consultation panel with request form and history tabs.
    Improved with better transitions and user feedback.
    """
    consultation_requested = pyqtSignal(object, str, str)
    consultation_cancelled = pyqtSignal(int)

    def __init__(self, student=None, parent=None):
        super().__init__(parent)
        self.student = student
        self.init_ui()

        # Set up optimized auto-refresh timer for history panel
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh_history)
        self.refresh_timer.start(120000)  # Reduced frequency: refresh every 2 minutes instead of 1

        # Connect tab change signal
        self.currentChanged.connect(self.on_tab_changed)

        # Set up MQTT monitoring for real-time updates (more important than polling)
        self.mqtt_check_timer = QTimer(self)
        self.mqtt_check_timer.timeout.connect(self.check_mqtt_status)
        self.mqtt_check_timer.start(60000)  # Reduced frequency: check every minute instead of 30 seconds
        
        # Track last refresh to avoid unnecessary updates
        self._last_refresh_time = 0
        self._min_refresh_interval = 30  # Minimum 30 seconds between refreshes

    def init_ui(self):
        """
        Initialize the consultation panel UI with improved styling and responsiveness.
        """
        # Import theme system
        from ..utils.theme import ConsultEaseTheme

        # Set object name for theme-based styling
        self.setObjectName("consultation_panel")

        # Create an enhanced stylesheet for the consultation panel
        enhanced_stylesheet = """
            QTabWidget#consultation_panel {
                background-color: #f8f9fa;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 5px;
                position: relative;
                top: 0px;  /* Ensure stable positioning */
            }

            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 4px;
                font-size: 15pt;
                font-weight: bold;
                min-width: 200px;
                min-height: 20px;  /* Ensure consistent tab height */
                position: relative;  /* Prevent floating */
            }

            QTabBar::tab:selected {
                background-color: #228be6;
                color: white;
                border: 1px solid #1971c2;
                border-bottom: none;
                position: relative;  /* Maintain position when selected */
            }

            QTabBar::tab:hover:!selected {
                background-color: #dee2e6;
                transition: background-color 0.2s ease;  /* Smooth hover transition */
            }

            QTabWidget::tab-bar {
                alignment: center;
                position: fixed;  /* Prevent tab bar from moving */
            }
            
            /* Ensure stable layout during interactions */
            QTabBar {
                qproperty-drawBase: false;
                outline: 0;  /* Remove focus outline that can cause shifting */
            }
        """

        # Apply the enhanced stylesheet
        self.setStyleSheet(enhanced_stylesheet)

        # Request form tab with improved icon and text
        self.request_form = ConsultationRequestForm()
        self.request_form.request_submitted.connect(self.handle_consultation_request)
        self.addTab(self.request_form, "Request Consultation")

        # Set tab icon if available
        try:
            from PyQt5.QtGui import QIcon
            self.setTabIcon(0, QIcon("central_system/resources/icons/request.png"))
        except:
            # If icon not available, just use text
            pass

        # History tab with improved icon and text
        self.history_panel = ConsultationHistoryPanel(self.student)
        self.history_panel.consultation_cancelled.connect(self.handle_consultation_cancel_from_history)
        self.addTab(self.history_panel, "Consultation History")

        # Set tab icon if available
        try:
            from PyQt5.QtGui import QIcon
            self.setTabIcon(1, QIcon("central_system/resources/icons/history.png"))
        except:
            # If icon not available, just use text
            pass

        # Calculate responsive minimum size based on screen dimensions
        screen_width = QApplication.desktop().screenGeometry().width()
        screen_height = QApplication.desktop().screenGeometry().height()

        # Calculate responsive minimum size (smaller on small screens, larger on big screens)
        min_width = min(900, max(500, int(screen_width * 0.5)))
        min_height = min(700, max(400, int(screen_height * 0.6)))

        self.setMinimumSize(min_width, min_height)

        # Set size policy for better responsiveness
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add smooth transition animation for tab changes
        self.setTabPosition(QTabWidget.North)
        self.tabBar().setDrawBase(False)

    def set_student(self, student):
        """
        Set the student for the consultation panel.
        """
        self.student = student
        self.history_panel.set_student(student)

        # Update window title with student name
        if student and hasattr(self.parent(), 'setWindowTitle'):
            # Handle both student object and student data dictionary
            if isinstance(student, dict):
                student_name = student.get('name', 'Student')
            else:
                # Legacy support for student objects
                student_name = getattr(student, 'name', 'Student')
            self.parent().setWindowTitle(f"ConsultEase - {student_name}")

    def set_faculty(self, faculty):
        """
        Set the faculty for the consultation request.
        Fixed to prevent jarring tab shifting.
        """
        self.request_form.set_faculty(faculty)

        # Switch to request form tab smoothly without animation
        # Only animate if we're not already on the request tab
        if self.currentIndex() != 0:
            # Set tab directly for immediate, stable transition
            self.setCurrentIndex(0)
            
            # Optional: Add a very subtle visual feedback without movement
            try:
                from PyQt5.QtCore import QTimer
                from PyQt5.QtGui import QColor
                
                # Brief highlight effect on the tab without position changes
                def highlight_tab():
                    tab_bar = self.tabBar()
                    original_color = tab_bar.palette().color(tab_bar.foregroundRole())
                    
                    # Set a subtle highlight
                    tab_bar.setTabTextColor(0, QColor("#228be6"))
                    
                    # Reset after very brief moment
                    def reset_color():
                        tab_bar.setTabTextColor(0, original_color)
                    
                    QTimer.singleShot(150, reset_color)
                
                # Apply highlight after a tiny delay to ensure tab switch is complete
                QTimer.singleShot(50, highlight_tab)
                
            except Exception as e:
                # If any issues with highlight, just ignore
                logger.debug(f"Tab highlight effect skipped: {e}")
                pass

    def set_faculty_options(self, faculty_list):
        """
        Set the available faculty options in the dropdown.
        """
        self.request_form.set_faculty_options(faculty_list)

        # Update status message if no faculty available
        if not faculty_list:
            QMessageBox.information(
                self,
                "No Faculty Available",
                "There are no faculty members available at this time. Please try again later."
            )

    def handle_consultation_request(self, faculty, message, course_code):
        """
        Handle consultation request submission with improved feedback.
        """
        try:
            # Try to import notification manager
            try:
                from ..utils.notification import NotificationManager, LoadingDialog
                use_notification_manager = True
            except ImportError:
                use_notification_manager = False

            # Define the operation to run with progress updates
            def submit_request(progress_callback=None):
                if progress_callback:
                    progress_callback(20, "Submitting request...")

                # Emit signal to controller
                self.consultation_requested.emit(faculty, message, course_code)

                if progress_callback:
                    progress_callback(60, "Processing submission...")

                # Clear form fields
                self.request_form.message_input.clear()
                self.request_form.course_input.clear()

                if progress_callback:
                    progress_callback(80, "Refreshing history...")

                # Refresh history
                self.history_panel.refresh_consultations()

                if progress_callback:
                    progress_callback(100, "Complete!")

                return True

            # Use loading dialog if available
            if use_notification_manager:
                # Show loading dialog while submitting
                LoadingDialog.show_loading(
                    self,
                    submit_request,
                    title="Submitting Request",
                    message="Submitting your consultation request...",
                    cancelable=False
                )

                # Show success message
                NotificationManager.show_message(
                    self,
                    "Request Submitted",
                    f"Your consultation request with {faculty.name} has been submitted successfully.",
                    NotificationManager.SUCCESS
                )
            else:
                # Fallback to basic implementation
                submit_request()

                # Show success message
                QMessageBox.information(
                    self,
                    "Consultation Request Submitted",
                    f"Your consultation request with {faculty.name} has been submitted successfully."
                )

            # Animate transition to history tab
            self.animate_tab_change(1)

        except Exception as e:
            logger.error(f"Error submitting consultation request: {str(e)}")

            # Show error message
            try:
                from ..utils.notification import NotificationManager
                NotificationManager.show_message(
                    self,
                    "Submission Error",
                    f"Failed to submit consultation request: {str(e)}",
                    NotificationManager.ERROR
                )
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to submit consultation request: {str(e)}"
                )

    @pyqtSlot(int)
    def handle_consultation_cancel_from_history(self, consultation_id):
        """
        Handles the consultation_cancelled signal from ConsultationHistoryPanel.
        This will then trigger the main cancellation logic in ConsultationPanel.
        """
        logger.info(f"ConsultationPanel: Received cancellation request from HistoryPanel for ID {consultation_id}. Forwarding...")
        # This now calls the main handler which also has confirmation, consider if one confirmation is enough.
        # For now, ConsultationPanel.handle_consultation_cancel will show its own confirmation.
        self.handle_consultation_cancel(consultation_id) 

    def handle_consultation_cancel(self, consultation_id):
        """
        Handle consultation cancellation with improved feedback.
        """
        try:
            # Try to import notification manager
            try:
                from ..utils.notification import NotificationManager, LoadingDialog
                use_notification_manager = True
            except ImportError:
                use_notification_manager = False

            # Define the operation to run with progress updates
            def cancel_consultation(progress_callback=None):
                if progress_callback:
                    progress_callback(30, "Cancelling request...")

                # Emit signal to controller
                self.consultation_cancelled.emit(consultation_id)

                if progress_callback:
                    progress_callback(70, "Updating records...")

                # Refresh history
                self.history_panel.refresh_consultations()

                if progress_callback:
                    progress_callback(100, "Complete!")

                return True

            # Use loading dialog if available
            if use_notification_manager:
                # Show confirmation dialog first
                if NotificationManager.show_confirmation(
                    self,
                    "Cancel Consultation",
                    "Are you sure you want to cancel this consultation request? This action cannot be undone.", # Made message more specific
                    "Yes, Cancel It",
                    "No, Keep Request"
                ):
                    # Show loading dialog while cancelling
                    LoadingDialog.show_loading(
                        self,
                        cancel_consultation,
                        title="Cancelling Request",
                        message="Cancelling your consultation request...",
                        cancelable=False
                    )

                    # Show success message
                    NotificationManager.show_message(
                        self,
                        "Request Cancelled",
                        "Your consultation request has been cancelled successfully.",
                        NotificationManager.SUCCESS
                    )
            else:
                # Fallback to basic implementation
                reply = QMessageBox.question(
                    self,
                    "Cancel Consultation",
                    "Are you sure you want to cancel this consultation request? This action cannot be undone.", # Made message more specific
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # Cancel the consultation (this emits the signal to the controller)
                    cancel_consultation()

                    # Show success message (moved after operation)
                    # QMessageBox.information(
                    # self,
                    # "Consultation Cancelled",
                    # "Your consultation request has been cancelled successfully."
                    # )
            # If loading dialog was used, success is shown within it or after.

        except Exception as e:
            logger.error(f"Error cancelling consultation: {str(e)}")

            # Show error message
            try:
                from ..utils.notification import NotificationManager
                NotificationManager.show_message(
                    self,
                    "Cancellation Error",
                    f"Failed to cancel consultation: {str(e)}",
                    NotificationManager.ERROR
                )
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to cancel consultation: {str(e)}"
                )

    def animate_tab_change(self, tab_index):
        """
        Animate the transition to a different tab with enhanced visual effects.
        Fixed to prevent jarring tab shifting and ensure stable navigation.

        Args:
            tab_index (int): The index of the tab to switch to
        """
        # Immediately change to the target tab to prevent any shifting issues
        self.setCurrentIndex(tab_index)
        
        # Apply a simple, subtle visual feedback without complex animations
        try:
            current_tab_bar = self.tabBar()
            if current_tab_bar and tab_index < current_tab_bar.count():
                # Store original style
                original_style = current_tab_bar.styleSheet()
                
                # Create a very subtle highlight effect
                highlight_style = f"""
                    QTabBar::tab:selected {{
                        background-color: #e3f2fd;
                        border-bottom: 3px solid #228be6;
                    }}
                """
                
                # Apply highlight temporarily
                current_tab_bar.setStyleSheet(highlight_style)
                
                # Reset after a very short delay
                def reset_style():
                    try:
                        current_tab_bar.setStyleSheet(original_style)
                    except:
                        pass
                
                QTimer.singleShot(150, reset_style)  # Very brief highlight
                
        except Exception as e:
            # If any error occurs, just ensure the tab is changed without animation
            logger.debug(f"Tab animation fallback: {e}")
            self.setCurrentIndex(tab_index)

    def on_tab_changed(self, index):
        """
        Handle tab change events.

        Args:
            index (int): The index of the newly selected tab
        """
        # Refresh history when switching to history tab
        if index == 1:  # History tab
            self.history_panel.refresh_consultations()

    def auto_refresh_history(self):
        """
        Automatically refresh the history panel periodically with intelligent timing.
        """
        current_time = time.time()
        
        # Check if enough time has passed since last refresh
        if current_time - self._last_refresh_time < self._min_refresh_interval:
            logger.debug("Skipping auto-refresh - too soon since last refresh")
            return
        
        # Only refresh if the history tab is visible and window is active
        if self.currentIndex() == 1:  # History tab
            # Check if parent window is active to avoid refreshing when not in use
            try:
                parent_window = self.window()
                if parent_window and (parent_window.isActiveWindow() or parent_window.isVisible()):
                    logger.debug("Auto-refreshing consultation history")
                    self.history_panel.refresh_consultations()
                    self._last_refresh_time = current_time
                else:
                    logger.debug("Skipping auto-refresh - window not active")
            except Exception as e:
                logger.debug(f"Error checking window state: {e}")
                # Fallback to refresh anyway
                self.history_panel.refresh_consultations()
                self._last_refresh_time = current_time
        else:
            logger.debug("Skipping auto-refresh - history tab not visible")

    def refresh_history(self):
        """
        Refresh the consultation history.
        """
        self.history_panel.refresh_consultations()

    def check_mqtt_status(self):
        """
        Check the status of the MQTT connection and handle accordingly.
        """
        if hasattr(self.history_panel, 'mqtt_client') and self.history_panel.mqtt_client:
            try:
                # Check if MQTT is still connected
                if not self.history_panel.mqtt_client.is_connected():
                    logger.warning("MQTT connection lost, attempting to reconnect...")
                    self.history_panel.setup_mqtt_monitoring()
            except Exception as e:
                logger.warning(f"MQTT status check error: {e}")
        elif not hasattr(self.history_panel, 'mqtt_client') or not self.history_panel.mqtt_client:
            # Try to establish MQTT connection if not present
            self.history_panel.setup_mqtt_monitoring()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """
        Callback for MQTT connection - DEPRECATED.
        Now handled by the centralized async MQTT service.
        """
        pass

    def on_mqtt_disconnect(self, client, userdata, rc):
        """
        Callback for MQTT disconnection - DEPRECATED.
        Now handled by the centralized async MQTT service.
        """
        pass

    def _schedule_mqtt_reconnect(self):
        """
        Schedule MQTT reconnection - DEPRECATED.
        Now handled by the centralized async MQTT service.
        """
        pass

    def _attempt_mqtt_reconnect(self):
        """
        Attempt to reconnect to MQTT broker - DEPRECATED.
        Now handled by the centralized async MQTT service.
        """
        pass

    def on_mqtt_message(self, client, userdata, msg):
        """
        Handle MQTT messages - DEPRECATED.
        Now using the centralized async MQTT service.
        """
        pass

    def _handle_consultation_update(self, response_data, topic):
        """
        Handle consultation-specific MQTT updates in the main thread.
        """
        if not self.student:
            return
            
        student_id = self.student.get('id') if isinstance(self.student, dict) else getattr(self.student, 'id', None)
        
        # Extract message details from different possible formats
        message_id = response_data.get('message_id', '') or response_data.get('consultation_id', '')
        response_type = response_data.get('response_type', '')
        faculty_id = response_data.get('faculty_id', '')
        faculty_name = response_data.get('faculty_name', 'Unknown Faculty')
        
        logger.info(f"Processing consultation update - Topic: {topic}, Response Type: {response_type}, Message ID: {message_id}, Faculty ID: {faculty_id}")
        
        # Check if any of our consultations match this response
        consultation_found = False
        
        # Handle different topic formats
        if 'consultease/faculty/' in topic and '/responses' in topic:
            # Extract faculty ID from topic: consultease/faculty/{id}/responses
            try:
                topic_parts = topic.split('/')
                topic_faculty_id = int(topic_parts[2])  # consultease/faculty/{ID}/responses
                
                # Check if this matches any of our consultations
                for consultation in self.consultations:
                    consultation_id_str = str(consultation.id)
                    consultation_faculty_id = getattr(consultation, 'faculty_id', None)
                    
                    # Match by message_id (consultation ID) or by faculty_id for pending consultations
                    if (message_id == consultation_id_str or 
                        (topic_faculty_id == consultation_faculty_id and consultation.status.value == 'pending')):
                        
                        logger.info(f"✅ Found matching consultation {consultation.id} for faculty response")
                        consultation_found = True
                        
                        # Show immediate notification
                        self.show_faculty_response_notification(response_type, faculty_name)
                        break
                        
            except (IndexError, ValueError) as e:
                logger.error(f"Error parsing faculty ID from topic {topic}: {e}")
        
        # Handle legacy professor/messages topic
        elif topic == 'professor/messages':
            # For professor/messages, we need to parse the message content
            # This might contain consultation information
            logger.info("Processing professor/messages topic")
            consultation_found = True  # Assume it's relevant for now
            
            # Show a generic notification
            self.show_faculty_response_notification('UPDATE', 'Faculty')
        
        # Handle other consultation topics
        elif 'consultation' in topic or 'responses' in topic:
            # Generic consultation update
            consultation_found = True
            self.show_faculty_response_notification(response_type or 'UPDATE', faculty_name)
        
        if consultation_found:
            # Schedule refresh after a short delay to allow database update
            QTimer.singleShot(2000, self.refresh_consultations)  # Increased delay to ensure DB is updated
            logger.info(f"Scheduled consultation history refresh due to faculty response")

    def _handle_status_update(self, response_data, topic):
        """
        Handle general status updates (faculty availability, etc.) in the main thread.
        """
        logger.debug(f"Processing status update: {response_data}")
        # Trigger a consultation refresh in case status affects pending consultations
        QTimer.singleShot(500, self.refresh_consultations)

    def show_faculty_response_notification(self, response_type, faculty_name):
        """
        Show notification when faculty responds via desk unit.
        """
        try:
            from ..utils.notification import NotificationManager
            
            if response_type.upper() in ['ACKNOWLEDGE', 'ACCEPTED']:
                title = "Consultation Accepted! ✅"
                message = f"{faculty_name} has accepted your consultation request."
                notification_type = NotificationManager.SUCCESS
            elif response_type.upper() in ['BUSY', 'UNAVAILABLE']:
                title = "Faculty Busy ⏳"
                message = f"{faculty_name} is currently busy and cannot take your consultation."
                notification_type = NotificationManager.WARNING
            else:
                title = "Consultation Update 📬"
                message = f"{faculty_name} has responded to your consultation request."
                notification_type = NotificationManager.INFO
                
            NotificationManager.show_message(
                self,
                title,
                message,
                notification_type
            )
            
        except ImportError:
            # Fallback to basic message box
            QMessageBox.information(
                self,
                "Faculty Response",
                f"{faculty_name} has responded to your consultation request. Please refresh to see the update."
            )
