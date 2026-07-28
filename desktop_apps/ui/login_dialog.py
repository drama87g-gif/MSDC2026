#!/usr/bin/env python3
"""
Login dialog for all desktop applications
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class LoginDialog(QDialog):
    """Login dialog for authentication"""
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_info = None
        
        self.init_ui()
        self.setModal(True)
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("MSDC Hospital - Login")
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Login")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)
        
        # Password
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Remember me
        self.remember_checkbox = QCheckBox("Remember me")
        layout.addWidget(self.remember_checkbox)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.do_login)
        button_layout.addWidget(login_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def do_login(self):
        """Perform login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password")
            return
        
        try:
            response = self.api_client.login(username, password)
            self.user_info = response.get('user')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Login Failed", f"Login error: {str(e)}")
