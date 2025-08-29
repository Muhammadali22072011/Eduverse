from datetime import datetime
from .user import db

class Role(db.Model):
    """Role model for defining user permissions"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Integer, default=0)  # Higher number = higher priority
    permissions = db.Column(db.JSON)  # Store permissions as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_roles = db.relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class UserRole(db.Model):
    """Many-to-many relationship between users and roles"""
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))  # For school-specific roles
    is_active = db.Column(db.Boolean, default=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='roles', foreign_keys=[user_id])
    role = db.relationship('Role', back_populates='user_roles')
    school = db.relationship('School', back_populates='user_roles')
    assigned_by_user = db.relationship('User', foreign_keys=[assigned_by])
    
    def __repr__(self):
        return f'<UserRole {self.user.username} -> {self.role.name}>'