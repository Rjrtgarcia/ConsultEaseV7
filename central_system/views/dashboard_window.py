from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGridLayout, QScrollArea, QFrame,
                               QLineEdit, QComboBox, QMessageBox, QTextEdit,
                               QSplitter, QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, QObject, pyqtSlot, QSettings
from PyQt5.QtGui import QPixmap, QIcon

import os
import logging
import time
from .base_window import BaseWindow
from .consultation_panel import ConsultationPanel
from ..utils.ui_components import FacultyCard
from ..ui.pooled_faculty_card import get_faculty_card_manager
from ..utils.ui_performance import (
    get_ui_batcher, get_widget_state_manager, SmartRefreshManager,
    batch_ui_update, timed_ui_update
)

# Set up logging
logger = logging.getLogger(__name__)


# Worker for fetching faculty data in a background thread
class FacultyFetcher(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, faculty_controller):
        super().__init__()
        self.faculty_controller = faculty_controller
        self.running = True

    @pyqtSlot()
    def run(self):
        if not self.running: # Check before starting
            return
        try:
            logger.info("FacultyFetcher: Starting to fetch faculty data.")
            # Assuming get_all_faculty fetches all necessary data without pagination for the dashboard
            # or handles pagination internally if needed for large datasets.
            # For simplicity here, fetching all.
            faculties = self.faculty_controller.get_all_faculty(page_size=1000) # Fetch a large number
            if self.running: # Check if still running before emitting
                self.finished.emit(faculties if faculties else [])
            logger.info(f"FacultyFetcher: Successfully fetched {len(faculties) if faculties else 0} faculties.")
        except Exception as e:
            logger.error(f"FacultyFetcher: Error fetching faculty data: {str(e)}")
            if self.running: # Check if still running
                self.error.emit(str(e))
        finally:
            logger.debug("FacultyFetcher: Run method finished.")
    
    def stop(self):
        logger.info("FacultyFetcher: Stopping.")
        self.running = False


class ConsultationRequestForm(QFrame):
    """
    Form to request a consultation with a faculty member.
    """
    request_submitted = pyqtSignal(object, str, str)

    def __init__(self, faculty=None, parent=None):
        super().__init__(parent)
        self.faculty = faculty
        self.init_ui()

    def init_ui(self):
        """
        Initialize the consultation request form UI.
        """
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet('''
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
        ''')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Form title
        title_label = QLabel("Request Consultation")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Faculty information
        if self.faculty:
            # Create a layout for faculty info with image
            faculty_info_layout = QHBoxLayout()

            # Faculty image
            image_label = QLabel()
            image_label.setFixedSize(60, 60)
            image_label.setStyleSheet("border: 1px solid #ddd; border-radius: 30px; background-color: white;")
            image_label.setScaledContents(True)

            # Try to load faculty image
            if hasattr(self.faculty, 'get_image_path') and self.faculty.image_path:
                try:
                    image_path = self.faculty.get_image_path()
                    if image_path and os.path.exists(image_path):
                        pixmap = QPixmap(image_path)
                        if not pixmap.isNull():
                            image_label.setPixmap(pixmap)
                except Exception as e:
                    logger.error(f"Error loading faculty image in consultation form: {str(e)}")

            faculty_info_layout.addWidget(image_label)

            # Faculty text info
            faculty_info = QLabel(f"Faculty: {self.faculty.name} ({self.faculty.department})")
            faculty_info.setStyleSheet("font-size: 14pt;")
            faculty_info_layout.addWidget(faculty_info)
            faculty_info_layout.addStretch()

            main_layout.addLayout(faculty_info_layout)
        else:
            # If no faculty is selected, show a dropdown
            faculty_label = QLabel("Select Faculty:")
            faculty_label.setStyleSheet("font-size: 14pt;")
            main_layout.addWidget(faculty_label)

            self.faculty_combo = QComboBox()
            self.faculty_combo.setStyleSheet("font-size: 14pt; padding: 8px;")
            # Faculty options would be populated separately
            main_layout.addWidget(self.faculty_combo)

        # Course code input
        course_label = QLabel("Course Code (optional):")
        course_label.setStyleSheet("font-size: 14pt;")
        main_layout.addWidget(course_label)

        self.course_input = QLineEdit()
        self.course_input.setStyleSheet("font-size: 14pt; padding: 8px;")
        main_layout.addWidget(self.course_input)

        # Message input
        message_label = QLabel("Consultation Details:")
        message_label.setStyleSheet("font-size: 14pt;")
        main_layout.addWidget(message_label)

        self.message_input = QTextEdit()
        self.message_input.setStyleSheet("font-size: 14pt; padding: 8px;")
        self.message_input.setMinimumHeight(150)
        main_layout.addWidget(self.message_input)

        # Submit button
        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                min-width: 120px;
            }
        ''')
        cancel_button.clicked.connect(self.cancel_request)

        submit_button = QPushButton("Submit Request")
        submit_button.setStyleSheet('''
            QPushButton {
                background-color: #4caf50;
                min-width: 120px;
            }
        ''')
        submit_button.clicked.connect(self.submit_request)

        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(submit_button)

        main_layout.addLayout(button_layout)

    def set_faculty(self, faculty):
        """
        Set the faculty for the consultation request.
        """
        self.faculty = faculty
        self.init_ui()

    def set_faculty_options(self, faculties):
        """
        Set the faculty options for the dropdown.
        Only show available faculty members.
        """
        if hasattr(self, 'faculty_combo'):
            self.faculty_combo.clear()
            available_count = 0

            for faculty in faculties:
                # Only add available faculty to the dropdown
                if hasattr(faculty, 'status') and faculty.status:
                    self.faculty_combo.addItem(f"{faculty.name} ({faculty.department})", faculty)
                    available_count += 1

            # Show a message if no faculty is available
            if available_count == 0:
                self.faculty_combo.addItem("No faculty members are currently available", None)

    def get_selected_faculty(self):
        """
        Get the selected faculty from the dropdown.
        """
        if hasattr(self, 'faculty_combo') and self.faculty_combo.count() > 0:
            return self.faculty_combo.currentData()
        return self.faculty

    def submit_request(self):
        """
        Handle the submission of the consultation request.
        """
        faculty = self.get_selected_faculty()
        if not faculty:
            QMessageBox.warning(self, "Consultation Request", "Please select a faculty member.")
            return

        # Check if faculty is available
        if hasattr(faculty, 'status') and not faculty.status:
            QMessageBox.warning(self, "Consultation Request",
                               f"Faculty {faculty.name} is currently unavailable. Please select an available faculty member.")
            return

        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Consultation Request", "Please enter consultation details.")
            return

        course_code = self.course_input.text().strip()

        # Emit signal with the request details
        self.request_submitted.emit(faculty, message, course_code)

    def cancel_request(self):
        """
        Cancel the consultation request.
        """
        self.message_input.clear()
        self.course_input.clear()
        self.setVisible(False)

class DashboardWindow(BaseWindow):
    """
    Main dashboard window with faculty availability display and consultation request functionality.
    """
    faculty_selected = pyqtSignal(object)  # Emits faculty data when selected
    consultation_requested = pyqtSignal(object, str, str)  # ✅ FIXED: Changed to emit (faculty, message, course_code)
    request_ui_refresh = pyqtSignal()
    logout_requested = pyqtSignal() # ✅ ADDED: Signal for logout request

    def __init__(self, student=None, parent=None, consultation_controller=None, faculty_controller=None):
        # Set all instance variables FIRST before calling super().__init__()
        # because BaseWindow.__init__() will call self.init_ui() which needs these variables
        self.student = student
        self.faculty_list = []
        self._last_faculty_data_list = []
        self.consultation_panel = None
        self.faculty_card_manager = get_faculty_card_manager()
        self.consultation_controller = consultation_controller
        self.faculty_controller = faculty_controller

        # For background faculty loading
        self._faculty_fetch_thread = None
        self._faculty_fetcher = None
        self._is_initial_load_pending = True

        # Call parent __init__ which will automatically call self.init_ui()
        # BaseWindow.__init__ will call self.init_ui(), so variables used by init_ui must be set before this.
        super().__init__(parent)
        
        # Now that self is a fully initialized QWidget, we can create QTimers with self as parent.
        # Debounce timer for full refreshes (if any)
        self._refresh_debounce_timer = QTimer(self)
        self._refresh_debounce_timer.setSingleShot(True)
        self._refresh_debounce_timer.timeout.connect(self._trigger_background_faculty_refresh)
        
        # Set up additional initialization after UI is created by super().__init__()
        
        # Set up smart refresh manager for optimized faculty status updates (periodic full sync)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(False) # Keep periodic
        self.refresh_timer.timeout.connect(self.request_background_faculty_refresh) # Request a background refresh
        
        # Initialize adaptive refresh logic - these are fine here
        self._consecutive_no_changes = 0
        self._max_refresh_interval = 600000  # Maximum 10 minutes
        self._min_refresh_interval = 180000   # Minimum 3 minutes
        self._last_faculty_hash = None
        self._last_update_time = time.time()

        # Connect signals with debouncing to prevent spam
        self.request_ui_refresh.connect(self._debounced_refresh)

        # UI performance utilities
        self.ui_batcher = get_ui_batcher()
        self.widget_state_manager = get_widget_state_manager()
        
        # Set faculty controller if provided (this will trigger MQTT setup and initial load)
        if self.faculty_controller:
            self.set_faculty_controller(self.faculty_controller)
        else:
            logger.warning("DashboardWindow initialized without FacultyController. Faculty list will not load initially via set_faculty_controller.")
            # Optionally, you could show an error or a placeholder if the controller is essential for basic operation
            # For now, it will just mean no data is loaded until controller is set and set_faculty_controller is called.

        # Start the periodic refresh timer only after the controller is potentially set and initial load might be triggered.
        # If faculty_controller is not set at init, set_faculty_controller must be called later.
        self.refresh_timer.start(self._min_refresh_interval) # Start with min interval

        logger.info("DashboardWindow __init__ completed.")

    def init_ui(self):
        """
        Initialize the main UI components of the dashboard.
        """
        # Get the specific stylesheet for the dashboard
        # ✅ FIX: Changed from get_current_theme() to get_dashboard_stylesheet()
        try:
            dashboard_stylesheet = ConsultEaseTheme.get_dashboard_stylesheet()
            self.setStyleSheet(dashboard_stylesheet) # Apply the stylesheet
            logger.debug("Dashboard stylesheet applied.")
        except AttributeError as e:
            logger.error(f"Failed to get or apply dashboard stylesheet: {e}")
            # Fallback or default styling if theme fails, or re-raise
            # For now, just logging, but consider a minimal default stylesheet.
        except Exception as e:
            logger.error(f"An unexpected error occurred while applying dashboard stylesheet: {e}")

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Welcome message using an environment variable for student name
        student_name = os.getenv('CONSULTEASE_STUDENT_NAME', self.student.get('name', 'Student') if self.student else 'Student')
        welcome_text = f"Welcome, {student_name}!"
        
        welcome_label = QLabel(welcome_text)
        welcome_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #DAA520;")
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet("font-size: 12pt; padding: 8px 15px; background-color: #D32F2F; color: white; border-radius: 5px;")
        logout_button.clicked.connect(self._request_logout) # ✅ CHANGED: Connect to the new method
        header_layout.addWidget(logout_button)
        
        main_layout.addWidget(header_widget)

        # Main content area (Splitter: Faculty Grid | Consultation Panel)
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left side: Faculty Grid
        faculty_grid_container = QWidget()
        faculty_grid_layout = QVBoxLayout(faculty_grid_container)
        faculty_grid_layout.setContentsMargins(0,0,0,0)


        # Filter and Search Bar
        filter_search_widget = QWidget()
        filter_search_layout = QHBoxLayout(filter_search_widget)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search faculty by name or department...")
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 5px; font-size: 11pt;")
        self.search_input.textChanged.connect(self.filter_faculty)
        filter_search_layout.addWidget(self.search_input)

        self.availability_filter_combo = QComboBox()
        self.availability_filter_combo.addItems(["All Faculty", "Available Only"])
        self.availability_filter_combo.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 5px; font-size: 11pt;")
        self.availability_filter_combo.currentIndexChanged.connect(self.filter_faculty)
        filter_search_layout.addWidget(self.availability_filter_combo)
        
        refresh_button = QPushButton("Refresh List")
        refresh_button.setStyleSheet("font-size: 11pt; padding: 8px 12px; background-color: #1976D2; color: white; border-radius: 5px;")
        refresh_button.clicked.connect(self.request_background_faculty_refresh) # Changed to request background refresh
        filter_search_layout.addWidget(refresh_button)

        faculty_grid_layout.addWidget(filter_search_widget)
        
        # Scroll area for faculty cards
        self.faculty_scroll_area = QScrollArea()
        self.faculty_scroll_area.setWidgetResizable(True)
        self.faculty_scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #ffffff; }")
        
        self.faculty_grid_widget = QWidget() # Widget to hold the grid layout
        self.faculty_grid_widget.setStyleSheet("background-color: #ffffff;")
        self.faculty_grid = QGridLayout(self.faculty_grid_widget)
        self.faculty_grid.setSpacing(10) 
        self.faculty_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft) # Align cards to top-left

        self.faculty_scroll_area.setWidget(self.faculty_grid_widget)
        faculty_grid_layout.addWidget(self.faculty_scroll_area)
        
        self.main_splitter.addWidget(faculty_grid_container)

        # Right side: Consultation Panel
        self.consultation_panel = ConsultationPanel(self.student)
        self.consultation_panel.setMinimumWidth(450) # Ensure it has a reasonable minimum width
        self.consultation_panel.setMaximumWidth(600) # And a maximum
        
        # Connect consultation panel signals
        self.consultation_panel.consultation_requested.connect(self._handle_consultation_request) # ✅ CHANGED: Connect to new method
        self.consultation_panel.consultation_cancelled.connect(self._handle_consultation_cancel) # ✅ FIXED: Connected to the correct method name with underscore
        
        self.main_splitter.addWidget(self.consultation_panel)
        
        # Set initial sizes for splitter
        # ✅ FIXED: Convert float values to integers with int()
        self.main_splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)] if self.width() > 0 else [600, 400])
        self.main_splitter.setCollapsible(0, False) # Prevent faculty grid from collapsing
        self.main_splitter.setCollapsible(1, True)  # Allow consultation panel to be collapsed

        # Restore previous splitter state if available
        self.restore_splitter_state()

        main_layout.addWidget(self.main_splitter)

        # Status bar (optional, for non-modal messages)
        self.status_bar_label = QLabel("Ready.")
        self.status_bar_label.setStyleSheet("padding: 5px; background-color: #eeeeee; border-top: 1px solid #cccccc;")
        main_layout.addWidget(self.status_bar_label)

        logger.info("Dashboard UI initialized.")
        # Initial data load is now handled by showEvent or a dedicated method after controller is set
        # self._perform_initial_faculty_load() # Moved

    def set_faculty_controller(self, controller):
        """Set the faculty controller and perform initial setup requiring it."""
        logger.info("DashboardWindow: Faculty controller set.")
        self.faculty_controller = controller
        # Now that controller is set, setup MQTT and load initial data
        self.setup_realtime_updates()
        self._perform_initial_faculty_load()

    def populate_faculty_grid_safe(self, faculty_data_list: list):
        """
        Safely populate the faculty grid using PooledFacultyCard.
        This method expects a list of faculty data dictionaries.
        """
        logger.info(f"Populating faculty grid with {len(faculty_data_list)} faculty members.")
        self._clear_faculty_grid_pooled() # Clear existing cards first

        if not faculty_data_list:
            self._show_empty_faculty_message()
            return

        # Update the main faculty list used for filtering
        # This should store dictionaries if get_all_faculty returns dicts, or convert them
        self._last_faculty_data_list = faculty_data_list # Assuming faculty_data_list is already list of dicts

        # Reset grid layout
        # While loop to remove all items from the grid layout
        while self.faculty_grid.count():
            item = self.faculty_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # It's managed by FacultyCardManager, so we don't delete here
                # but ensure it's hidden if not reused immediately
                widget.hide()


        row, col = 0, 0
        # Determine number of columns based on available width (e.g., 3-4 cards per row)
        # This is a simplified example; a more robust solution might use flow layout or recalculate on resize
        num_columns = max(1, self.faculty_scroll_area.width() // 300) if self.faculty_scroll_area.width() > 0 else 3

        for faculty_data in faculty_data_list:
            if not isinstance(faculty_data, dict):
                logger.warning(f"Skipping faculty item, expected dict, got {type(faculty_data)}")
                continue
            
            # Ensure faculty_data has an 'id'
            faculty_id = faculty_data.get('id')
            if faculty_id is None:
                logger.warning(f"Skipping faculty item due to missing ID: {faculty_data.get('name')}")
                continue

            try:
                # The consultation callback is show_consultation_form
                card = self.faculty_card_manager.get_faculty_card(faculty_data, self.show_consultation_form)
                if card:
                    self.faculty_grid.addWidget(card, row, col)
                    col += 1
                    if col >= num_columns:
                        col = 0
                        row += 1
                else:
                    logger.warning(f"Failed to get faculty card for {faculty_data.get('name')}")
            except Exception as e:
                logger.error(f"Error creating faculty card for {faculty_data.get('name')}: {e}")
                import traceback
                logger.error(traceback.format_exc())


        # Add stretch to the end to ensure cards align to the top-left
        self.faculty_grid.setRowStretch(row + 1, 1)
        self.faculty_grid.setColumnStretch(num_columns, 1)
        
        # Update the scroll area
        self.faculty_grid_widget.adjustSize() # Adjust size of the container widget
        self.faculty_scroll_area.setWidget(self.faculty_grid_widget) # Re-set widget if necessary

        # Update filter options (if faculty_list contains full objects)
        # self.consultation_panel.set_faculty_options(self.faculty_list)
        # Assuming faculty_data_list are dicts; if full objects are needed by consultation_panel, adjust accordingly
        # For now, ConsultationPanel is likely populated by ConsultationController directly or another mechanism.

        logger.info("Faculty grid population complete.")
        self._scroll_faculty_to_top()
        self.status_bar_label.setText(f"Displaying {len(faculty_data_list)} faculty members. Last updated: {time.strftime('%I:%M:%S %p')}")

    def show_consultation_form_safe(self, faculty_data: dict):
        """
        Show consultation form using safe faculty data dictionary.

        Args:
            faculty_data (dict or int): Faculty data dictionary or faculty ID
        """
        try:
            # Handle case where faculty_data might be an integer (faculty ID)
            if isinstance(faculty_data, int):
                logger.debug(f"Received faculty ID {faculty_data}, need to fetch faculty data")
                # Try to get faculty data from current faculty list
                faculty_id = faculty_data
                
                # Find faculty data in the currently loaded faculty list
                target_faculty_data = None
                if hasattr(self, '_last_faculty_data_list') and self._last_faculty_data_list:
                    for f_data in self._last_faculty_data_list:
                        if f_data.get('id') == faculty_id:
                            target_faculty_data = f_data
                            break
                
                if target_faculty_data:
                    faculty_data = target_faculty_data
                else:
                    logger.error(f"Could not find faculty data for ID {faculty_id}")
                    return
            
            # Ensure faculty_data is a dictionary
            if not isinstance(faculty_data, dict):
                logger.error(f"Invalid faculty_data type: {type(faculty_data)}. Expected dict or int.")
                return
                
            # Validate required fields
            required_fields = ['id', 'name']
            for field in required_fields:
                if field not in faculty_data:
                    logger.error(f"Missing required field '{field}' in faculty_data")
                    return

            # Create a mock faculty object for compatibility
            class MockFaculty:
                def __init__(self, data):
                    self.id = data['id']
                    self.name = data['name']
                    self.department = data.get('department', 'Unknown Department')
                    self.status = data.get('status', 'Unknown')
                    self.email = data.get('email', '')
                    self.room = data.get('room', None)

            mock_faculty = MockFaculty(faculty_data)
            self.show_consultation_form(mock_faculty)
            
        except Exception as e:
            faculty_name = "Unknown"
            if isinstance(faculty_data, dict):
                faculty_name = faculty_data.get('name', 'Unknown')
            elif isinstance(faculty_data, int):
                faculty_name = f"Faculty ID {faculty_data}"
            
            logger.error(f"Error showing consultation form for faculty {faculty_name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def _extract_safe_faculty_data(self, faculty_data_list):
        """
        Convert faculty model objects to a list of dictionaries suitable for UI and caching.
        Ensures all necessary fields are present with defaults.
        """
        safe_faculties = []
        for faculty_obj in faculty_data_list:
            status_val = getattr(faculty_obj, 'status', False) # Default to False (offline)
            # Convert common string statuses from DB/model to unified dashboard statuses
            if isinstance(status_val, str):
                status_str_lower = status_val.lower()
                if status_str_lower in ["available", "online", "present"]:
                    actual_status_for_card = "available"
                    is_available_bool = True
                elif status_str_lower in ["busy", "in_consultation"]:
                    actual_status_for_card = status_str_lower # busy or in_consultation
                    is_available_bool = False # Cannot request if busy/in_consultation via main button
                else:
                    actual_status_for_card = "offline"
                    is_available_bool = False
            elif isinstance(status_val, bool):
                is_available_bool = status_val
                actual_status_for_card = "available" if status_val else "offline"
            else: # Default for unknown types
                is_available_bool = False
                actual_status_for_card = "offline"

            data = {
                'id': faculty_obj.id,
                'name': getattr(faculty_obj, 'name', "Unknown Faculty"),
                'department': getattr(faculty_obj, 'department', "N/A"),
                'available': is_available_bool, # This is for button enablement
                'status': actual_status_for_card, # This is for status indicator dot
                'email': getattr(faculty_obj, 'email', "N/A"),
                'room': getattr(faculty_obj, 'room_number', "N/A"), # Assuming room_number attribute
                'image_path': getattr(faculty_obj, 'image_path', None)
            }
            safe_faculties.append(data)
        return safe_faculties

    def populate_faculty_grid(self, faculties: list):
        """
        Populate the faculty grid with faculty cards.
        Optimized for performance with batch processing and reduced UI updates.

        Args:
            faculties (list): List of faculty objects
        """
        # Log faculty data for debugging
        logger.info(f"Populating faculty grid with {len(faculties) if faculties else 0} faculty members")
        if faculties:
            for faculty in faculties:
                try:
                    # Access attributes safely to avoid DetachedInstanceError
                    faculty_name = faculty.name
                    faculty_status = faculty.status
                    faculty_always_available = getattr(faculty, 'always_available', False)
                    logger.debug(f"Faculty: {faculty_name}, Status: {faculty_status}, Always Available: {faculty_always_available}")
                except Exception as e:
                    logger.warning(f"Error accessing faculty attributes: {e}")
                    continue

        # Temporarily disable updates to reduce flickering and improve performance
        self.setUpdatesEnabled(False)

        try:
            # Clear existing grid efficiently using pooled cards
            self._clear_faculty_grid_pooled()

            # Handle empty faculty list
            if not faculties:
                logger.info("No faculty members found - showing empty state message")
                self._show_empty_faculty_message()
                return

            # Calculate optimal number of columns based on screen width
            screen_width = QApplication.desktop().screenGeometry().width()

            # Fixed card width (matches the width set in FacultyCard)
            card_width = 280  # Updated to match the improved FacultyCard width

            # Grid spacing (matches the spacing set in faculty_grid)
            spacing = 15

            # Get the actual width of the faculty grid container
            grid_container_width = self.faculty_grid.parentWidget().width()
            if grid_container_width <= 0:  # If not yet available, estimate based on screen
                grid_container_width = int(screen_width * 0.6)  # 60% of screen for faculty grid

            # Account for grid margins
            grid_container_width -= 30  # 15px left + 15px right margin

            # Calculate how many cards can fit in a row, accounting for spacing
            max_cols = max(1, int(grid_container_width / (card_width + spacing)))

            # Adjust for very small screens
            if screen_width < 800:
                max_cols = 1  # Force single column on very small screens

            # Add faculty cards to grid with centering containers
            row, col = 0, 0

            # Create all widgets first before adding to layout (batch processing)
            containers = []

            logger.info(f"Creating faculty cards for {len(faculties)} faculty members")

            for faculty in faculties:
                try:
                    # Create a container widget to center the card
                    container = QWidget()
                    container.setStyleSheet("background-color: transparent;")
                    container_layout = QHBoxLayout(container)
                    container_layout.setContentsMargins(0, 0, 0, 0)
                    container_layout.setAlignment(Qt.AlignCenter)

                    # Convert faculty object to dictionary format expected by FacultyCard
                    # Access all attributes at once to avoid DetachedInstanceError
                    faculty_id = faculty.id
                    faculty_name = faculty.name
                    faculty_department = faculty.department
                    faculty_status = faculty.status
                    faculty_always_available = getattr(faculty, 'always_available', False)
                    faculty_email = getattr(faculty, 'email', '')
                    faculty_room = getattr(faculty, 'room', None)

                    faculty_data = {
                        'id': faculty_id,
                        'name': faculty_name,
                        'department': faculty_department,
                        'available': faculty_status,
                        'status': 'Available' if faculty_status else 'Unavailable',
                        'email': faculty_email,
                        'room': faculty_room
                    }

                    logger.debug(f"Creating card for faculty {faculty.name}: available={faculty_data['available']}, status={faculty_data['status']}")

                    # Get pooled faculty card
                    card = self.faculty_card_manager.get_faculty_card(
                        faculty_data,
                        consultation_callback=lambda f_data=faculty_data: self.show_consultation_form_safe(f_data)
                    )

                    # Connect consultation signal if it exists
                    if hasattr(card, 'consultation_requested'):
                        # Use faculty_data dictionary instead of faculty object to avoid type mismatch
                        card.consultation_requested.connect(lambda f_data=faculty_data: self.show_consultation_form_safe(f_data))

                    # Add card to container
                    container_layout.addWidget(card)

                    # Store container for batch processing
                    containers.append((container, row, col))

                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

                    logger.debug(f"Successfully created card for faculty {faculty.name}")

                except Exception as e:
                    logger.error(f"Error creating faculty card for {faculty.name}: {e}")
                    continue

            # Now add all containers to the grid at once
            for container, r, c in containers:
                self.faculty_grid.addWidget(container, r, c)

            # Log successful population
            logger.info(f"Successfully populated faculty grid with {len(containers)} faculty cards")

        finally:
            # Re-enable updates after all changes are made
            self.setUpdatesEnabled(True)

    def _show_empty_faculty_message(self):
        """
        Show a message when no faculty members are available.
        """
        logger.info("Showing empty faculty message")

        # Create a message widget
        message_widget = QWidget()
        message_widget.setMinimumHeight(300)  # Ensure it's visible
        message_layout = QVBoxLayout(message_widget)
        message_layout.setAlignment(Qt.AlignCenter)
        message_layout.setSpacing(20)

        # Title
        title_label = QLabel("No Faculty Members Available")
        title_label.setObjectName("empty_state_title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel#empty_state_title {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px;
                padding: 20px;
            }
        """)
        message_layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Faculty members need to be added through the admin dashboard.\nOnce added, they will appear here when available for consultation.\n\nPlease contact your administrator to add faculty members.")
        desc_label.setObjectName("empty_state_desc")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel#empty_state_desc {
                font-size: 18px;
                color: #7f8c8d;
                margin: 10px 20px;
                padding: 20px;
                line-height: 1.6;
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 2px solid #e9ecef;
            }
        """)
        message_layout.addWidget(desc_label)

        # Add some spacing
        message_layout.addStretch()

        # Add the message widget to the grid - span all columns
        self.faculty_grid.addWidget(message_widget, 0, 0, 1, self.faculty_grid.columnCount() if self.faculty_grid.columnCount() > 0 else 1)

    def _show_loading_indicator(self):
        """
        Show a non-modal loading message in the faculty grid area.
        """
        self._clear_faculty_grid_pooled()
        # Add a QLabel to the grid
        if not hasattr(self, '_loading_label') or self._loading_label is None:
            self._loading_label = QLabel("🔄 Loading faculty data, please wait...")
            self._loading_label.setAlignment(Qt.AlignCenter)
            self._loading_label.setStyleSheet("font-size: 16pt; color: #888888; padding: 50px;")
        
        # Ensure any previous content is cleared if faculty_grid is used directly
        while self.faculty_grid.count():
            item = self.faculty_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater() # Or hide() if pooled/managed elsewhere

        self.faculty_grid.addWidget(self.faculty_label_placeholder if hasattr(self, 'faculty_label_placeholder') else self._loading_label, 0, 0, 1, 3) # Span across columns
        self._loading_label.show()
        self.status_bar_label.setText("🔄 Loading faculty data...")
        logger.debug("Loading indicator shown.")

    def _hide_loading_indicator(self):
        """
        Hide the non-modal loading message.
        """
        if hasattr(self, '_loading_label') and self._loading_label is not None:
            self._loading_label.hide()
            # Optionally remove it from layout if it was added directly
            # self.faculty_grid.removeWidget(self._loading_label)
        # The faculty grid will be populated, replacing the label.
        logger.debug("Loading indicator hidden.")

    def _show_error_message(self, error_text):
        """
        Show an error message in the faculty grid.

        Args:
            error_text (str): Error message to display
        """
        logger.info(f"Showing error message: {error_text}")

        # Clear existing grid first
        self._clear_faculty_grid_pooled()

        # Create error widget
        error_widget = QWidget()
        error_widget.setMinimumHeight(250)
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignCenter)
        error_layout.setSpacing(15)

        # Error title
        error_title = QLabel("⚠️ Error Loading Faculty Data")
        error_title.setAlignment(Qt.AlignCenter)
        error_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #e74c3c;
                padding: 15px;
            }
        """)
        error_layout.addWidget(error_title)

        # Error message
        error_message = QLabel(error_text)
        error_message.setAlignment(Qt.AlignCenter)
        error_message.setWordWrap(True)
        error_message.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 10px 20px;
                background-color: #fdf2f2;
                border: 2px solid #f5c6cb;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        error_layout.addWidget(error_message)

        # Retry instruction
        retry_label = QLabel("The system will automatically retry in a few moments.\nIf the problem persists, please contact your administrator.")
        retry_label.setAlignment(Qt.AlignCenter)
        retry_label.setWordWrap(True)
        retry_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #95a5a6;
                padding: 10px;
                font-style: italic;
            }
        """)
        error_layout.addWidget(retry_label)

        # Add to grid
        self.faculty_grid.addWidget(error_widget, 0, 0, 1, 1)

    def filter_faculty(self):
        """
        Filter faculty based on search term and availability.
        Uses the self._last_faculty_data_list which should contain dicts.
        """
        if not hasattr(self, '_last_faculty_data_list') or not self._last_faculty_data_list:
            logger.debug("Filter faculty called but no base data available.")
            # Optionally trigger a refresh if data is missing
            # self.request_background_faculty_refresh()
            return

        search_term = self.search_input.text().lower()
        filter_available_only = self.availability_filter_combo.currentText() == "Available Only"

        filtered_list = []
        for faculty_data in self._last_faculty_data_list:
            name_match = search_term in faculty_data.get('name', '').lower()
            dept_match = search_term in faculty_data.get('department', '').lower()
            status_match = not filter_available_only or faculty_data.get('status', 'offline').lower() == 'available'
            
            if (name_match or dept_match) and status_match:
                filtered_list.append(faculty_data)
        
        logger.debug(f"Filtering complete. Found {len(filtered_list)} matching faculty members.")
        self.populate_faculty_grid_safe(filtered_list) # Repopulate with dicts

    def _perform_filter(self):
        """
        Perform filtering with proper error handling.
        """
        try:
            from ..controllers import FacultyController
            
            filter_text = self.search_input.text().strip().lower()
            show_available = self.availability_filter_combo.currentText() == "Available Only"
            
            faculty_controller = FacultyController()
            faculties = faculty_controller.get_all_faculty()
            
            # Convert to safe faculty data format
            safe_faculties = []
            for faculty in faculties:
                faculty_data = {
                    'id': faculty.id,
                    'name': faculty.name,
                    'department': faculty.department,
                    'available': faculty.status,
                    'status': 'Available' if faculty.status else 'Unavailable',
                    'email': faculty.email,
                    'room': getattr(faculty, 'room', None)
                }
                safe_faculties.append(faculty_data)
            
            # Apply filters
            if filter_text:
                safe_faculties = [f for f in safe_faculties if filter_text in f['name'].lower() or filter_text in f['department'].lower()]
            
            if show_available:
                safe_faculties = [f for f in safe_faculties if f['available']]
            
            # Use safe population method
            self.populate_faculty_grid_safe(safe_faculties)
            
        except Exception as e:
            logger.error(f"Error performing filter: {str(e)}")
            self._show_error_message(f"Filter error: {str(e)}")

    def refresh_faculty_status(self):
        """
        DEPRECATED in favor of request_background_faculty_refresh.
        This method is kept for compatibility if directly called but should not be primary.
        """
        logger.warning("DEPRECATED: refresh_faculty_status() called. Use request_background_faculty_refresh().")
        self.request_background_faculty_refresh()

    def request_background_faculty_refresh(self):
        """
        Request a faculty list refresh, which will be run in the background.
        Uses a debounce timer to prevent rapid successive calls.
        """
        logger.info("Background faculty refresh requested.")
        self.status_bar_label.setText("🔄 Requesting faculty list update...")
        # Debouncer will call _trigger_background_faculty_refresh
        self._refresh_debounce_timer.start(500) # 500ms debounce time

    def _trigger_background_faculty_refresh(self):
        """
        Actually triggers the background refresh operation.
        Called by the debounce timer.
        """
        logger.info("Triggering background faculty refresh operation.")
        if not self.faculty_controller:
            logger.error("Cannot refresh faculty: FacultyController not set.")
            self.status_bar_label.setText("❌ Error: System not ready for refresh.")
            return

        if self._faculty_fetch_thread and self._faculty_fetch_thread.isRunning():
            logger.warning("Faculty fetch operation already in progress. Skipping new request.")
            self.status_bar_label.setText("⏳ Refresh already in progress.")
            return

        self._show_loading_indicator() # Show non-modal loading message

        # Recreate thread and worker for cleanliness if needed, or manage single instance
        if self._faculty_fetch_thread and self._faculty_fetch_thread.isRunning():
             self._faculty_fetcher.stop() # Request previous to stop
             self._faculty_fetch_thread.quit()
             self._faculty_fetch_thread.wait(1000) # Wait a bit

        self._faculty_fetch_thread = QThread(self)
        self._faculty_fetcher = FacultyFetcher(self.faculty_controller)
        self._faculty_fetcher.moveToThread(self._faculty_fetch_thread)

        self._faculty_fetcher.finished.connect(self._handle_faculty_loaded)
        self._faculty_fetcher.error.connect(self._handle_faculty_load_error)
        self._faculty_fetch_thread.started.connect(self._faculty_fetcher.run)
        # Clean up thread when it finishes
        self._faculty_fetch_thread.finished.connect(self._faculty_fetch_thread.deleteLater)
        self._faculty_fetcher.finished.connect(self._faculty_fetch_thread.quit) # Ensure thread quits
        self._faculty_fetcher.error.connect(self._faculty_fetch_thread.quit)

        logger.info("Starting faculty fetch thread.")
        self._faculty_fetch_thread.start()

    @pyqtSlot(list)
    def _handle_faculty_loaded(self, faculty_list_from_worker):
        """Handles the faculty data once fetched by the background worker."""
        logger.info(f"Faculty data received from worker: {len(faculty_list_from_worker)} items.")
        self._hide_loading_indicator()

        # Convert model objects to dictionaries for cards
        faculty_data_for_cards = self._extract_safe_faculty_data(faculty_list_from_worker)
        self.faculty_list = faculty_list_from_worker # Store raw model objects if needed elsewhere

        # Check for changes before full repopulation (for adaptive timer)
        current_data_str = "".join(f"{fd.get('id')}:{fd.get('status')}" for fd in faculty_data_for_cards)
        new_hash = hashlib.md5(current_data_str.encode()).hexdigest() if current_data_str else None

        if self._last_faculty_hash == new_hash and not self._is_initial_load_pending:
            logger.info("No changes in faculty data since last refresh.")
            self._consecutive_no_changes += 1
            self.status_bar_label.setText(f"Faculty list up-to-date. Last checked: {time.strftime('%I:%M:%S %p')}")
        else:
            logger.info("Faculty data has changed or initial load, repopulating grid.")
            self._consecutive_no_changes = 0
            self.populate_faculty_grid_safe(faculty_data_for_cards) # Pass the list of dicts
            self._last_faculty_hash = new_hash
            # self._last_faculty_data_list is updated within populate_faculty_grid_safe if it's the source of truth
            # For filtering, ensure self._last_faculty_data_list is updated here if populate doesn't do it.
            self._last_faculty_data_list = faculty_data_for_cards # Ensure this is updated for filtering


        self._last_update_time = time.time()
        self._is_initial_load_pending = False

        # Adjust refresh timer based on changes
        if self._consecutive_no_changes >= 3:
            new_interval = min(self.refresh_timer.interval() * 2, self._max_refresh_interval)
            self.refresh_timer.setInterval(new_interval)
            logger.info(f"No changes for {self._consecutive_no_changes} cycles. Refresh interval increased to {new_interval / 1000}s.")
        else:
            self.refresh_timer.setInterval(self._min_refresh_interval)

        # Clean up worker and thread if they are one-shot per request
        if self._faculty_fetcher:
            self._faculty_fetcher.stop() # Signal fetcher to stop if it has loops
            # self._faculty_fetcher.deleteLater() # Let Qt manage deletion after events processed
            # self._faculty_fetcher = None
        # if self._faculty_fetch_thread:
            # self._faculty_fetch_thread.quit() # Already connected to quit on finish
            # self._faculty_fetch_thread.wait(500) # Give it a moment
            # self._faculty_fetch_thread = None
        logger.info("Finished handling loaded faculty data.")

    @pyqtSlot(str)
    def _handle_faculty_load_error(self, error_message):
        """Handles errors from the faculty fetcher."""
        logger.error(f"Error loading faculty data from worker: {error_message}")
        self._hide_loading_indicator()
        self._show_error_message(f"Failed to load faculty: {error_message}")
        self.status_bar_label.setText(f"❌ Error loading faculty: {error_message}")
        self._is_initial_load_pending = False # Allow next attempt
         # Clean up worker and thread if they are one-shot per request
        if self._faculty_fetcher:
            self._faculty_fetcher.stop()
        # if self._faculty_fetch_thread:
        #     self._faculty_fetch_thread.quit()
        #     self._faculty_fetch_thread.wait(500)

    def show_consultation_form(self, faculty_or_id):
        """
        Show the consultation request form for a specific faculty.

        Args:
            faculty_or_id (object or int): Faculty object or Faculty ID
        """
        logger.debug(f"show_consultation_form called with: {faculty_or_id} (type: {type(faculty_or_id)})")
        faculty_object = None

        if isinstance(faculty_or_id, int):
            logger.info(f"show_consultation_form received faculty ID: {faculty_or_id}. Fetching object.")
            try:
                from ..controllers import FacultyController # Local import to avoid circular dependency issues at module load
                fc = FacultyController()
                faculty_object = fc.get_faculty_by_id(faculty_or_id)
                if not faculty_object:
                    logger.warning(f"Faculty with ID {faculty_or_id} not found by controller.")
                    self.show_notification(
                        f"Faculty with ID {faculty_or_id} not found.",
                        "error"
                    )
                    return
            except Exception as e:
                logger.error(f"Error fetching faculty by ID {faculty_or_id} in show_consultation_form: {str(e)}")
                self.show_notification(
                    f"Error retrieving details for faculty ID {faculty_or_id}.",
                    "error"
                )
                return
        elif hasattr(faculty_or_id, 'status') and hasattr(faculty_or_id, 'name') and hasattr(faculty_or_id, 'id'): # Basic check for Faculty-like object
            logger.debug("show_consultation_form received a faculty-like object.")
            faculty_object = faculty_or_id
        else:
            logger.error(f"show_consultation_form called with invalid/unexpected type: {type(faculty_or_id)}, value: {faculty_or_id}")
            self.show_notification("An unexpected error occurred while trying to show the consultation form. Invalid faculty data.", "error")
            return

        # Now use faculty_object for the rest of the method
        if not faculty_object.status:
            self.show_notification(
                f"Faculty {faculty_object.name} (ID: {faculty_object.id}) is currently unavailable for consultation.",
                "error"
            )
            return

        # Also populate the dropdown with all available faculty
        try:
            from ..controllers import FacultyController # Local import
            faculty_controller = FacultyController()
            available_faculty = faculty_controller.get_all_faculty(filter_available=True)

            # Set the faculty and faculty options in the consultation panel
            self.consultation_panel.set_faculty(faculty_object) # Use the validated/fetched object
            self.consultation_panel.set_faculty_options(available_faculty)
        except Exception as e:
            logger.error(f"Error loading available faculty for consultation form: {str(e)}")
            self.show_notification("Error preparing consultation form.", "error")

    def _scroll_faculty_to_top(self):
        """Scroll the faculty grid to the top."""
        if self.faculty_scroll_area and self.faculty_scroll_area.verticalScrollBar():
            self.faculty_scroll_area.verticalScrollBar().setValue(0)

    def _clear_faculty_grid_pooled(self):
        """Clear all faculty cards from the grid and return them to the pool."""
        logger.debug("Clearing faculty grid using FacultyCardManager.")
        # Iterate over grid items, get faculty_id from card, and return to manager
        for i in reversed(range(self.faculty_grid.count())):
            item = self.faculty_grid.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if isinstance(card, PooledFacultyCard) and card.faculty_id is not None:
                    self.faculty_card_manager.return_faculty_card(card.faculty_id)
                else:
                    # If it's not a pooled card or ID is missing, just remove/delete
                    widget = self.faculty_grid.takeAt(i).widget()
                    if widget: widget.deleteLater()
            # else: # If item is a spacer or layout, remove it differently if needed
            #     self.faculty_grid.removeItem(item)

        # Fallback: ensure manager knows all cards are cleared if grid manipulation is complex
        # self.faculty_card_manager.clear_all_cards() # This is more aggressive
        logger.debug("Faculty grid cleared.")

    def showEvent(self, event):
        """
        Handle window show event to trigger initial faculty data loading and real-time updates.
        """
        # Call parent showEvent first
        super().showEvent(event)

        # Set up real-time updates when dashboard becomes visible
        self.setup_realtime_updates()

        # Load faculty data immediately when the window is first shown
        # Only do this if we haven't loaded faculty data yet
        if not hasattr(self, '_initial_load_done') or not self._initial_load_done:
            logger.info("Dashboard window shown - triggering initial faculty data load")
            self._initial_load_done = True

            # Schedule the initial faculty load after a short delay to ensure UI is ready
            QTimer.singleShot(100, self._perform_initial_faculty_load)

    def _perform_initial_faculty_load(self):
        """
        Perform the initial loading of faculty data.
        Now uses the background thread mechanism.
        """
        logger.info("Performing initial faculty load using background worker.")
        self.status_bar_label.setText("🔄 Loading initial faculty data...")
        self._is_initial_load_pending = True
        # This will show loading indicator and start the thread via _trigger_background_faculty_refresh
        self._trigger_background_faculty_refresh()

    def closeEvent(self, event):
        """
        Handle window close event with proper cleanup.
        """
        # Clean up faculty card manager
        if hasattr(self, 'faculty_card_manager'):
            self.faculty_card_manager.clear_all_cards()

        # Save splitter state before closing
        self.save_splitter_state()

        # Unsubscribe from MQTT topics
        self.cleanup_realtime_updates()

        # Call parent close event
        super().closeEvent(event)

    def setup_realtime_updates(self):
        """
        Set up real-time MQTT subscription for faculty status updates with improved reliability.
        """
        try:
            from ..utils.mqtt_utils import subscribe_to_topic
            
            logger.info(f"🔥🔥🔥 DASHBOARD setup_realtime_updates CALLED")
            
            # Subscribe to faculty status updates using the centralized utils
            topics = [
                "consultease/faculty/+/status",  # ✅ PRIMARY: What desk units actually publish to
                "faculty/+/status",              # Legacy compatibility
                "faculty/+/availability",        # Alternative availability topic
                "consultation/+/status",         # Consultation status updates
                "consultease/system/notifications",  # System-wide notifications
            ]
            
            logger.info(f"🔥🔥🔥 DASHBOARD subscribing to topics: {topics}")
            
            for topic in topics:
                try:
                    logger.info(f"🔥🔥🔥 DASHBOARD subscribing to topic: {topic}")
                    result = subscribe_to_topic(topic, self.handle_realtime_status_update)
                    logger.info(f"🔥🔥🔥 DASHBOARD subscription result for {topic}: {result}")
                except Exception as e:
                    logger.error(f"🔥🔥🔥 DASHBOARD failed to subscribe to topic {topic}: {e}")
                    import traceback
                    logger.error(f"🔥🔥🔥 DASHBOARD subscription traceback: {traceback.format_exc()}")
                    
            logger.info("🔥🔥🔥 DASHBOARD completed real-time faculty status subscriptions")
        except Exception as e:
            logger.error(f"🔥🔥🔥 DASHBOARD error setting up real-time updates: {e}")
            import traceback
            logger.error(f"🔥🔥🔥 DASHBOARD setup traceback: {traceback.format_exc()}")

    def cleanup_realtime_updates(self):
        """
        Clean up real-time MQTT subscriptions.
        """
        try:
            from ..services.async_mqtt_service import get_async_mqtt_service
            
            mqtt_service = get_async_mqtt_service()
            if mqtt_service:
                # Unsubscribe from topics
                topics = [
                    "consultease/faculty/+/status",
                    "faculty/+/status",
                    "faculty/+/availability", 
                    "consultation/+/status",
                    "consultease/system/notifications",
                ]
                
                for topic in topics:
                    try:
                        mqtt_service.unregister_topic_handler(topic)
                        logger.debug(f"Unsubscribed from topic: {topic}")
                    except Exception as e:
                        logger.error(f"Failed to unsubscribe from topic {topic}: {e}")
                        
                logger.info("Cleaned up real-time subscriptions")
        except Exception as e:
            logger.error(f"Error cleaning up real-time updates: {e}")

    def handle_realtime_status_update(self, topic, data):
        """
        Handle real-time status updates from MQTT with thread-safe GUI updates.
        """
        # Add debugging to confirm this method is being called
        logger.info(f"🔥🔥🔥 DASHBOARD handle_realtime_status_update CALLED - Topic: {topic}, Data: {data}")
        
        # Schedule the actual processing in the main thread to prevent Qt threading violations
        QTimer.singleShot(0, lambda: self._process_realtime_status_update(topic, data))

    def _process_realtime_status_update(self, topic, data):
        """
        Process real-time status updates in the main thread.
        Optimized to update individual cards directly.
        """
        try:
            logger.info(f"Dashboard processing MQTT: Topic: {topic}, Data: {data}")
            topic_parts = topic.split('/')

            # Handle primary faculty status topic: consultease/faculty/{id}/status
            if "consultease/faculty" in topic and topic.endswith("/status") and len(topic_parts) == 4:
                try:
                    faculty_id = int(topic_parts[2])
                    new_status_str = "offline" # Default status

                    if isinstance(data, dict):
                        # Enhanced status extraction based on typical desk unit payload
                        is_present = data.get('present', False) # Desk unit might send 'present'
                        status_from_payload = data.get('status', 'offline').lower() # And a 'status' string like 'AVAILABLE', 'BUSY'
                        # detailed_status = data.get('detailed_status', status_from_payload)

                        if is_present:
                            if status_from_payload == 'busy' or status_from_payload == 'in_consultation':
                                new_status_str = status_from_payload
                            else: # present and not explicitly busy -> available
                                new_status_str = "available"
                        else: # Not present or no 'present' field
                            new_status_str = "offline"
                        
                        logger.info(f"Updating faculty card {faculty_id} to status: {new_status_str} based on payload: {data}")
                        self.faculty_card_manager.update_faculty_status(faculty_id, new_status_str)
                        self.status_bar_label.setText(f"Faculty {faculty_id} status updated to {new_status_str}. ({time.strftime('%I:%M:%S %p')})")
                        # No full refresh needed here, individual card is updated.

                    elif isinstance(data, str): # Handle simple string status like "true", "false", "available", "offline"
                        status_lower = data.lower()
                        if status_lower == "true" or status_lower == "available":
                            new_status_str = "available"
                        elif status_lower == "false" or status_lower == "offline":
                            new_status_str = "offline"
                        elif status_lower == "busy":
                            new_status_str = "busy"
                        else:
                            logger.warning(f"Unknown string status for faculty {faculty_id}: {data}")
                            new_status_str = "offline" # Default for unknown string
                        
                        logger.info(f"Updating faculty card {faculty_id} to status: {new_status_str} based on string payload: {data}")
                        self.faculty_card_manager.update_faculty_status(faculty_id, new_status_str)
                        self.status_bar_label.setText(f"Faculty {faculty_id} status updated to {new_status_str}. ({time.strftime('%I:%M:%S %p')})")

                    else:
                        logger.warning(f"Unexpected data format for faculty status {faculty_id}: {type(data)}, data: {data}")
                        
                except (IndexError, ValueError) as e:
                    logger.error(f"Error parsing faculty ID or status from topic {topic}, data {data}: {e}")
            
            # Handle legacy faculty status topics (can still trigger a debounced full refresh if necessary)
            elif "faculty/" in topic and ("/status" in topic or "/availability" in topic):
                logger.info(f"Legacy faculty status update on topic {topic}. Triggering debounced full refresh.")
                self._debounced_refresh() # Keep debounced full refresh for less specific legacy topics

            # Handle consultation status updates for the ConsultationPanel
            elif "consultation/" in topic and "/status" in topic:
                logger.info(f"Consultation status update on topic {topic}. Refreshing history panel.")
                if hasattr(self, 'consultation_panel') and self.consultation_panel:
                    self.consultation_panel.refresh_history() # This is already relatively targeted
                    # Optionally, show a non-modal notification if the update is for the current student
                    # This requires parsing student_id from the payload if available
                    self.show_notification("A consultation status has been updated.", "info") 

            elif "consultease/system/notifications" in topic:
                if isinstance(data, dict):
                    notification_type = data.get('type', 'unknown')
                    message = data.get('message', 'System notification received.')
                    level = data.get('level', 'info').lower()
                    logger.info(f"System notification: Type: {notification_type}, Msg: {message}, Lvl: {level}")
                    self.show_notification(message, level) # Use dashboard's notification system

                    # If it's a faculty status related system notification, might still do selective update or light refresh
                    if notification_type == 'faculty_status_changed' and 'faculty_id' in data and 'new_status' in data:
                        faculty_id = data['faculty_id']
                        new_status = data['new_status']
                        logger.info(f"System notification indicates faculty {faculty_id} changed to {new_status}. Updating card.")
                        self.faculty_card_manager.update_faculty_status(faculty_id, new_status)
                        self.status_bar_label.setText(f"Faculty {faculty_id} status updated. ({time.strftime('%I:%M:%S %p')})")
                    elif notification_type == 'general_refresh_request': # Example of a system-wide refresh trigger
                        logger.info("System notification requests a general UI refresh.")
                        self.request_background_faculty_refresh()
                        
        except Exception as e:
            logger.error(f"🔥🔥🔥 Error handling real-time status update: {e}")
            import traceback
            logger.error(f"🔥🔥🔥 Traceback: {traceback.format_exc()}")

    def _debounced_refresh(self):
        """
        Handle the debounced refresh signal to prevent spam updates.
        """
        logger.info(f"🔥🔥🔥 _debounced_refresh CALLED")
        # Cancel any pending refresh
        self._refresh_debounce_timer.stop()
        # Schedule a new refresh after a short delay
        self._refresh_debounce_timer.start(500)  # 500ms debounce
        logger.info(f"🔥🔥🔥 _debounced_refresh scheduled refresh in 500ms")

    def _request_logout(self): # ✅ ADDED: Method to emit logout signal
        """Emits the logout_requested signal."""
        logger.info("Logout requested by user.")
        self.logout_requested.emit()

    def _handle_consultation_request(self, faculty, message, course_code): # ✅ ADDED: New method to handle consultation requests
        """
        Handles consultation requests from the consultation panel.
        Re-emits the request via the dashboard's signal.
        
        Args:
            faculty: The faculty object or data
            message: The consultation message/details
            course_code: The course code (optional)
        """
        try:
            # We no longer need to extract faculty_id since we're forwarding the entire faculty object
            logger.info(f"Handling consultation request for faculty: {getattr(faculty, 'name', None) or faculty.get('name', 'Unknown')}")
            
            # Forward all parameters to the main application handler
            self.consultation_requested.emit(faculty, message, course_code)
            
        except Exception as e:
            logger.error(f"Error handling consultation request: {str(e)}")
            
    def _handle_consultation_cancel(self, consultation_id): # ✅ ADDED: Placeholder for the handle_consultation_cancel method
        """
        Handles consultation cancellation requests from the consultation panel.
        This is a placeholder - implement actual functionality as needed.
        
        Args:
            consultation_id: The ID of the consultation to cancel
        """
        logger.info(f"Consultation cancellation requested for ID: {consultation_id}")
        # Implementation needed - for example, calling a controller method
        
    def save_splitter_state(self):
        """
        Save the current splitter state to application settings.
        """
        try:
            settings = QSettings("ConsultEase", "ConsultEaseSystem")
            settings.setValue("dashboard/splitter_state", self.main_splitter.saveState())
            logger.debug("Saved splitter state")
        except Exception as e:
            logger.error(f"Error saving splitter state: {e}")
            
    def restore_splitter_state(self):
        """
        Restore the splitter state from application settings.
        If no saved state exists, the current state is maintained.
        """
        try:
            settings = QSettings("ConsultEase", "ConsultEaseSystem")
            splitter_state = settings.value("dashboard/splitter_state")
            
            if splitter_state:
                success = self.main_splitter.restoreState(splitter_state)
                if success:
                    logger.debug("Restored splitter state from settings")
                else:
                    logger.warning("Failed to restore splitter state (invalid data), using defaults")
            else:
                logger.debug("No saved splitter state found, using defaults")
                
        except Exception as e:
            logger.error(f"Error restoring splitter state: {e}")
            # The default state set earlier will remain
        
