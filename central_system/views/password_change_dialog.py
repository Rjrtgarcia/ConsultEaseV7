"""
Password change dialog for ConsultEase admin interface.
Handles forced password changes and regular password updates.
"""
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

from ..utils.ui_components import ModernButton
from ..utils.theme import ConsultEaseTheme

logger = logging.getLogger(__name__)


class PasswordChangeDialog(QDialog):
    """
    Dialog for changing admin passwords with validation and security features.
    """
    password_changed = pyqtSignal(bool)  # Emits True if password was changed successfully

    def __init__(self, admin_info, forced_change=False, parent=None):
        super().__init__(parent)
        self.admin_info = admin_info
        self.forced_change = forced_change
        self.init_ui()

    def init_ui(self):
        """Initialize the password change dialog UI with improved styling and layout."""
        self.setWindowTitle("Change Password")
        self.setModal(True)
        self.setMinimumSize(520, 650)  # Reduced from potentially larger size
        self.setMaximumSize(600, 750)  # Set max size for better control

        # Apply enhanced dialog styling
        enhanced_dialog_stylesheet = """
            QDialog {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 12px;
            }
            QLabel {
                color: #212529;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;  /* Reduced padding */
                font-size: 13pt;  /* Slightly smaller font */
                background-color: #ffffff;
                color: #212529;
                min-height: 18px;  /* Reduced height */
            }
            QLineEdit:focus {
                border-color: #0d6efd;
                background-color: #f8f9ff;
                outline: none;
            }
            QLineEdit:invalid {
                border-color: #dc3545;
                background-color: #fff5f5;
            }
            QFrame {
                border-radius: 8px;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px 20px;  /* Reduced padding */
                font-size: 13pt;  /* Slightly smaller font */
                min-width: 100px;  /* Reduced min width */
                min-height: 38px;  /* Reduced height */
            }
            QPushButton:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
        """
        self.setStyleSheet(enhanced_dialog_stylesheet)

        # Main layout with optimized spacing
        layout = QVBoxLayout(self)
        layout.setSpacing(18)  # Reduced from 25
        layout.setContentsMargins(30, 25, 30, 25)  # Reduced margins

        # Header
        self.create_header(layout)

        # Password form
        self.create_password_form(layout)

        # Password requirements (compact version)
        self.create_requirements_section(layout)

        # Password strength indicator
        self.create_strength_indicator(layout)

        # Buttons
        self.create_buttons(layout)

        # Set focus to current password field
        self.current_password_input.setFocus()

    def create_header(self, layout):
        """Create the dialog header with improved styling."""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #0d6efd, stop: 1 #0a58ca);
                border-radius: 10px;
                padding: 16px;  /* Reduced padding */
                margin-bottom: 8px;  /* Reduced margin */
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 16, 16, 16)  # Reduced margins
        header_layout.setSpacing(8)  # Reduced spacing

        # Title with better typography
        title_label = QLabel("🔐 Change Password")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))  # Slightly smaller
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; margin-bottom: 6px;")

        # Subtitle based on forced change with improved styling
        if self.forced_change:
            subtitle_text = "⚠️ Your password has expired and must be changed before continuing."
            subtitle_color = "#fff3cd"
            subtitle_bg = "background-color: rgba(255, 193, 7, 0.2); border-radius: 6px; padding: 6px;"
        else:
            subtitle_text = f"👤 Changing password for: {self.admin_info.get('username', 'Unknown')}"
            subtitle_color = "rgba(255, 255, 255, 0.9)"
            subtitle_bg = ""

        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setFont(QFont("Segoe UI", 11))  # Slightly smaller
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {subtitle_color}; {subtitle_bg}")
        subtitle_label.setWordWrap(True)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)

        layout.addWidget(header_frame)

    def create_password_form(self, layout):
        """Create the password input form with enhanced UX."""
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;  /* Reduced padding */
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(16)  # Reduced spacing

        # Current password section
        current_section = QVBoxLayout()
        current_section.setSpacing(6)  # Reduced spacing
        current_label = QLabel("🔑 Current Password:")
        current_label.setFont(QFont("Segoe UI", 11, QFont.Bold))  # Slightly smaller
        current_label.setStyleSheet("color: #495057; margin-bottom: 3px;")
        
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)
        self.current_password_input.setPlaceholderText("Enter your current password")
        self.current_password_input.textChanged.connect(self.validate_form)
        
        current_section.addWidget(current_label)
        current_section.addWidget(self.current_password_input)

        # New password section
        new_section = QVBoxLayout()
        new_section.setSpacing(6)  # Reduced spacing
        new_label = QLabel("🆕 New Password:")
        new_label.setFont(QFont("Segoe UI", 11, QFont.Bold))  # Slightly smaller
        new_label.setStyleSheet("color: #495057; margin-bottom: 3px;")
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Enter your new password")
        self.new_password_input.textChanged.connect(self.validate_form)
        self.new_password_input.textChanged.connect(self.update_strength_indicator)
        
        new_section.addWidget(new_label)
        new_section.addWidget(self.new_password_input)

        # Confirm password section
        confirm_section = QVBoxLayout()
        confirm_section.setSpacing(6)  # Reduced spacing
        confirm_label = QLabel("✅ Confirm New Password:")
        confirm_label.setFont(QFont("Segoe UI", 11, QFont.Bold))  # Slightly smaller
        confirm_label.setStyleSheet("color: #495057; margin-bottom: 3px;")
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm your new password")
        self.confirm_password_input.textChanged.connect(self.validate_form)
        
        confirm_section.addWidget(confirm_label)
        confirm_section.addWidget(self.confirm_password_input)

        # Add sections to form layout
        form_layout.addLayout(current_section)
        form_layout.addLayout(new_section)
        form_layout.addLayout(confirm_section)

        layout.addWidget(form_frame)

    def create_requirements_section(self, layout):
        """Create password requirements section with better visual design."""
        req_frame = QFrame()
        req_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #fff8e1, stop: 1 #fffbf0);
                border: 2px solid #ffd54f;
                border-radius: 10px;
                padding: 16px;  /* Reduced padding */
            }
        """)
        req_layout = QVBoxLayout(req_frame)
        req_layout.setSpacing(6)  # Reduced spacing

        req_title = QLabel("📋 Password Requirements")
        req_title.setFont(QFont("Segoe UI", 11, QFont.Bold))  # Slightly smaller
        req_title.setStyleSheet("color: #f57f17; margin-bottom: 8px;")
        req_layout.addWidget(req_title)

        # Create a more compact requirements list
        requirements_items = [
            "• At least 8 characters long",
            "• Contains uppercase letters (A-Z)",
            "• Contains lowercase letters (a-z)",
            "• Contains numbers (0-9)",
            "• Contains special characters (!@#$%^&*)"
        ]

        # Use a horizontal layout for first three items to save space
        row1_layout = QVBoxLayout()
        row1_layout.setSpacing(2)
        
        for i, requirement in enumerate(requirements_items):
            req_item = QLabel(requirement)
            req_item.setFont(QFont("Segoe UI", 10))  # Smaller font
            req_item.setStyleSheet("color: #f57f17; margin: 1px 0px; margin-left: 8px;")
            row1_layout.addWidget(req_item)

        req_layout.addLayout(row1_layout)
        layout.addWidget(req_frame)

    def create_strength_indicator(self, layout):
        """Create a password strength indicator."""
        strength_frame = QFrame()
        strength_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;  /* Reduced padding */
            }
        """)
        strength_layout = QVBoxLayout(strength_frame)
        strength_layout.setSpacing(6)  # Reduced spacing

        strength_title = QLabel("💪 Password Strength:")
        strength_title.setFont(QFont("Segoe UI", 10, QFont.Bold))  # Smaller font
        strength_title.setStyleSheet("color: #495057;")
        strength_layout.addWidget(strength_title)

        # Progress bar for strength
        self.strength_progress = QProgressBar()
        self.strength_progress.setRange(0, 100)
        self.strength_progress.setValue(0)
        self.strength_progress.setMaximumHeight(8)  # Thinner progress bar
        self.strength_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #e9ecef;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #dc3545;
                border-radius: 3px;
            }
        """)
        strength_layout.addWidget(self.strength_progress)

        # Strength label
        self.strength_label = QLabel("Enter a password to check strength")
        self.strength_label.setFont(QFont("Segoe UI", 9))  # Smaller font
        self.strength_label.setStyleSheet("color: #6c757d;")
        self.strength_label.setAlignment(Qt.AlignCenter)
        strength_layout.addWidget(self.strength_label)

        layout.addWidget(strength_frame)

    def create_buttons(self, layout):
        """Create dialog buttons with improved styling."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)  # Reduced spacing

        # Cancel button (only if not forced change)
        if not self.forced_change:
            self.cancel_button = ModernButton("Cancel")
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            self.cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        # Change password button
        self.change_button = ModernButton("🔐 Change Password", primary=True)
        self.change_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #28a745, stop: 1 #1e7e34);
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #34ce57, stop: 1 #28a745);
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.change_button.clicked.connect(self.change_password)
        self.change_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.change_button)

        # Add some top margin for the button section
        button_container = QVBoxLayout()
        button_container.setContentsMargins(0, 12, 0, 0)  # Top margin only
        button_container.addLayout(button_layout)
        
        layout.addLayout(button_container)

    def validate_form(self):
        """Validate the form and enable/disable the change button."""
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Check if all fields are filled
        all_filled = all([current_password, new_password, confirm_password])

        # Check if passwords match
        passwords_match = new_password == confirm_password

        # Check password strength
        password_valid = self.validate_password_strength(new_password)

        # Enable button only if all conditions are met
        self.change_button.setEnabled(all_filled and passwords_match and password_valid)

    def validate_password_strength(self, password):
        """Validate password strength according to requirements."""
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return all([has_upper, has_lower, has_digit, has_special])

    def change_password(self):
        """Handle password change request."""
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Final validation
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return

        if not self.validate_password_strength(new_password):
            QMessageBox.warning(self, "Error", "New password does not meet strength requirements.")
            return

        # Disable button and show progress
        self.change_button.setEnabled(False)
        self.change_button.setText("Changing Password...")

        try:
            # Import admin controller
            from ..controllers.admin_controller import AdminController
            admin_controller = AdminController()

            # Attempt password change
            success, errors = admin_controller.change_password(
                self.admin_info['id'],
                current_password,
                new_password
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Password changed successfully!"
                )
                
                # Clear the password fields for security
                self.current_password_input.clear()
                self.new_password_input.clear()
                self.confirm_password_input.clear()
                
                # Emit success signal
                self.password_changed.emit(True)
                
                # Ensure admin object refresh by adding a small delay
                QTimer.singleShot(100, self.accept)
            else:
                error_message = "\n".join(errors) if errors else "Password change failed."
                QMessageBox.warning(self, "Error", error_message)

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "An unexpected error occurred while changing the password."
            )
        finally:
            # Re-enable button
            self.change_button.setEnabled(True)
            self.change_button.setText("�� Change Password")

    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.forced_change:
            # Don't allow closing if password change is forced
            reply = QMessageBox.question(
                self,
                "Password Change Required",
                "You must change your password before continuing. Are you sure you want to exit the application?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Exit the entire application
                from PyQt5.QtWidgets import QApplication
                QApplication.quit()
            else:
                event.ignore()
        else:
            event.accept()

    def update_strength_indicator(self):
        """Update the password strength indicator based on the current password."""
        password = self.new_password_input.text()
        
        if not password:
            self.strength_progress.setValue(0)
            self.strength_label.setText("Enter a password to check strength")
            self.strength_label.setStyleSheet("color: #6c757d;")
            return

        # Calculate strength score
        score = 0
        feedback = []

        # Length check
        if len(password) >= 8:
            score += 20
        else:
            feedback.append("needs 8+ characters")

        # Character type checks
        if any(c.isupper() for c in password):
            score += 20
        else:
            feedback.append("needs uppercase")

        if any(c.islower() for c in password):
            score += 20
        else:
            feedback.append("needs lowercase")

        if any(c.isdigit() for c in password):
            score += 20
        else:
            feedback.append("needs numbers")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 20
        else:
            feedback.append("needs special characters")

        # Update progress bar
        self.strength_progress.setValue(score)

        # Update label and colors
        if score < 40:
            strength_text = "Weak"
            color = "#dc3545"
            progress_color = "#dc3545"
        elif score < 80:
            strength_text = "Fair"
            color = "#fd7e14"
            progress_color = "#fd7e14"
        elif score < 100:
            strength_text = "Good"
            color = "#20c997"
            progress_color = "#20c997"
        else:
            strength_text = "Strong"
            color = "#28a745"
            progress_color = "#28a745"

        # Update progress bar color
        self.strength_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #e9ecef;
            }}
            QProgressBar::chunk {{
                background-color: {progress_color};
                border-radius: 3px;
            }}
        """)

        # Set label text
        if feedback:
            label_text = f"{strength_text} - {', '.join(feedback)}"
        else:
            label_text = f"{strength_text} password!"

        self.strength_label.setText(label_text)
        self.strength_label.setStyleSheet(f"color: {color}; margin-top: 5px; font-weight: bold;")
