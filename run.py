#!/usr/bin/env python3
"""
EduVerse Platform Runner Script
"""

import os
import sys
from app import create_app, init_db

def main():
    """Main entry point for the application"""
    # Set environment
    os.environ['FLASK_ENV'] = 'development'
    
    # Create application
    app = create_app('development')
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

if __name__ == '__main__':
    main()