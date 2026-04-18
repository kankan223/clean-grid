"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-04-17 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, comment='User email for login'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='bcrypt hashed password'),
        sa.Column('display_name', sa.String(length=100), nullable=False, comment='Public-facing name'),
        sa.Column('role', sa.Enum('CITIZEN', 'CREW', 'ADMIN', name='userrole'), nullable=False, comment='User role: citizen, crew, or admin'),
        sa.Column('total_points', sa.Integer(), nullable=False, comment='Total accumulated points'),
        sa.Column('badge_tier', sa.Enum('CLEANER', 'GUARDIAN', 'HERO', name='badgetier'), nullable=True, comment='Computed badge tier based on points'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When user account was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When user was last updated'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('ix_users_total_points'), 'users', ['total_points'], unique=False)
    
    # Create incidents table with PostGIS location
    op.create_table('incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('location', postgresql.GEOGRAPHY(geometry_type='POINT', srid=4326), nullable=True, comment='Geographic point location (lat/lng)'),
        sa.Column('image_url', sa.Text(), nullable=False, comment='URL to before-photo in object storage'),
        sa.Column('after_image_url', sa.Text(), nullable=True, comment='URL to after-photo'),
        sa.Column('address_text', sa.Text(), nullable=True, comment='Reverse-geocoded or user-provided address'),
        sa.Column('note', sa.Text(), nullable=True, comment='Optional user note (max 200 chars)'),
        sa.Column('waste_detected', sa.Boolean(), nullable=True, comment='AI result - was waste detected?'),
        sa.Column('confidence', sa.Float(), nullable=True, comment='AI confidence score (0-1)'),
        sa.Column('severity', sa.String(length=10), nullable=True, comment='AI-derived severity: None, Low, Medium, High'),
        sa.Column('bounding_boxes', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Optional array of bounding box coordinates'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='Current incident status'),
        sa.Column('priority_score', sa.Float(), nullable=True, comment='Computed priority score (0-100)'),
        sa.Column('is_hotspot', sa.Boolean(), nullable=False, comment='Whether in a known hotspot zone'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When incident was reported'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When incident was last updated'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_assigned_to'), 'incidents', ['assigned_to'], unique=False)
    op.create_index(op.f('ix_incidents_created_at'), 'incidents', ['created_at'], unique=False)
    op.create_index(op.f('ix_incidents_priority_score'), 'incidents', ['priority_score'], unique=False)
    op.create_index(op.f('ix_incidents_reporter_id'), 'incidents', ['reporter_id'], unique=False)
    op.create_index(op.f('ix_incidents_status'), 'incidents', ['status'], unique=False)
    # Create GIST index for geographic queries
    op.execute('CREATE INDEX ix_incidents_location ON incidents USING GIST (location)')
    # Create point_transactions table
    op.create_table('point_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, comment='User who received points'),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Related incident (if applicable)'),
        sa.Column('points', sa.Integer(), nullable=False, comment='Positive point value awarded'),
        sa.Column('reason', sa.Enum('REPORT_CONFIRMED', 'CLEANUP_VERIFIED', 'REPORT_BONUS', name='pointreason'), nullable=False, comment='Reason for point award'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When points were awarded'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_point_transactions_user_id'), 'point_transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_point_transactions_created_at'), 'point_transactions', ['created_at'], unique=False)
    
    # Create routes table for route optimization
    op.create_table('routes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, comment='User who created the route'),
        sa.Column('incident_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Array of incident UUIDs in order'),
        sa.Column('polyline_geojson', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='GeoJSON LineString of route path'),
        sa.Column('total_distance_km', sa.Float(), nullable=True, comment='Total route distance in kilometers'),
        sa.Column('estimated_duration_min', sa.Integer(), nullable=True, comment='Estimated duration in minutes'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='Route status: Active, Completed, Archived'),
        sa.Column('is_approximate', sa.Boolean(), nullable=False, comment='True if using fallback algorithm instead of ORS'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When route was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When route was last updated'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_routes_created_by'), 'routes', ['created_by'], unique=False)
    op.create_index(op.f('ix_routes_created_at'), 'routes', ['created_at'], unique=False)
    op.create_index(op.f('ix_routes_status'), 'routes', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('routes')
    op.drop_table('point_transactions')
    op.drop_table('incidents')
    op.drop_table('users')
