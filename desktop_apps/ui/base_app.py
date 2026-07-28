#!/usr/bin/env python3
"""
Base PyQt5 application class for all desktop applications
"""

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QStatusBar, QMenuBar, QMenu
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont

from config import get_config
from api_client import APIClient
from ui.login_dialog import LoginDialog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BaseApplication(QMainWindow):
    """Base class for all desktop applications"""
    
    APP_NAME = "MSDC Hospital"
    APP_VERSION = "3.0.0"
    
    def __init__(self, app_type: str):
        super().__init__()
        self.app_type = app_type
        self.config = get_config()
        self.api_client = None
        self.user = None
        
        self.init_ui()
        self.setup_api()
        self.check_connection()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle(f"{self.APP_NAME} - {self.app_type.title()} | v{self.APP_VERSION}")
        self.setGeometry(100, 100, self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Initializing...")
        self.status_bar.addWidget(self.status_label)
        
        # Setup connection timer
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(30000)  # Check every 30 seconds
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        settings_action = tools_menu.addAction('Settings')
        settings_action.triggered.connect(self.open_settings)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
    
    def setup_api(self):
        """Setup API client"""
        self.api_client = APIClient(
            base_url=self.config.API_BASE_URL,
            timeout=self.config.API_TIMEOUT
        )
    
    def check_connection(self):
        """Check API connection status"""
        if self.api_client.check_health():
            self.status_label.setText("✅ Connected")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("❌ Disconnected")
            self.status_label.setStyleSheet("color: red;")
    
    def authenticate(self):
        """Show login dialog and authenticate"""
        login_dialog = LoginDialog(self.api_client, parent=self)
        if login_dialog.exec_():
            self.user = login_dialog.user_info
            logger.info(f"User {self.user['username']} logged in")
            self.on_login_success()
            return True
        else:
            QMessageBox.warning(self, "Authentication Failed", "Login cancelled or failed")
            return False
    
    def on_login_success(self):
        """Called when user successfully logs in"""
        self.status_label.setText(f"✅ Logged in as {self.user['username']}")
    
    def open_settings(self):
        """Open application settings"""
        QMessageBox.information(self, "Settings", "Settings not implemented yet")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About MSDC Hospital",
            f"""<h2>MSDC Hospital Management System</h2>
            <p>Version {self.APP_VERSION}</p>
            <p>Department: {self.app_type.title()}</p>
            <p>© 2026 MSDC Hospital. All rights reserved.</p>"""
        )
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.user:
            reply = QMessageBox.question(
                self,
                'Exit Application',
                'Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.api_client.logout()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BaseApplication("demo")
    window.show()
    sys.exit(app.exec_())
