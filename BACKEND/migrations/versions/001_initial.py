"""initial

Revision ID: 001_initial
Revises: 
Create Date: 2026-06-25 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='student'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create internship_jobs table
    op.create_table(
        'internship_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('company_rating', sa.Float(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('stipend', sa.Float(), nullable=True),
        sa.Column('duration_months', sa.Integer(), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('required_skills', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('preferred_qualifications', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('application_url', sa.String(length=500), nullable=True),
        sa.Column('jsearch_job_id', sa.String(length=255), nullable=True),
        sa.Column('posted_date', sa.String(length=50), nullable=True),
        sa.Column('application_deadline', sa.String(length=50), nullable=True),
        sa.Column('job_status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('embedding_vector', sa.ARRAY(sa.Float()), nullable=True),
        sa.Column('embedding_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_internship_jobs_company_name'), 'internship_jobs', ['company_name'], unique=False)
    op.create_index(op.f('ix_internship_jobs_job_title'), 'internship_jobs', ['job_title'], unique=False)
    op.create_index(op.f('ix_internship_jobs_jsearch_job_id'), 'internship_jobs', ['jsearch_job_id'], unique=True)
    op.create_index(op.f('ix_internship_jobs_location'), 'internship_jobs', ['location'], unique=False)

    # Create welfare_schemes table
    op.create_table(
        'welfare_schemes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scheme_type', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('eligibility_criteria', sa.JSON(), nullable=True),
        sa.Column('provider', sa.String(length=255), nullable=False),
        sa.Column('application_deadline', sa.String(length=50), nullable=True),
        sa.Column('application_url', sa.String(length=500), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('benefits', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('documents_required', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('processing_time', sa.String(length=100), nullable=True),
        sa.Column('scheme_status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('embedding_vector', sa.ARRAY(sa.Float()), nullable=True),
        sa.Column('embedding_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_welfare_schemes_name'), 'welfare_schemes', ['name'], unique=False)
    op.create_index(op.f('ix_welfare_schemes_provider'), 'welfare_schemes', ['provider'], unique=False)
    op.create_index(op.f('ix_welfare_schemes_scheme_type'), 'welfare_schemes', ['scheme_type'], unique=False)

    # Create interview_sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=True),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('messages_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['internship_jobs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_sessions_session_id'), 'interview_sessions', ['session_id'], unique=True)
    op.create_index(op.f('ix_interview_sessions_user_id'), 'interview_sessions', ['user_id'], unique=False)

    # Create interview_feedbacks table
    op.create_table(
        'interview_feedbacks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('user_answer', sa.Text(), nullable=False),
        sa.Column('technical_accuracy', sa.Float(), nullable=False),
        sa.Column('communication_clarity', sa.Float(), nullable=False),
        sa.Column('relevance_to_job', sa.Float(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=False),
        sa.Column('improvement_areas', sa.JSON(), nullable=False),
        sa.Column('sample_answer', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_feedbacks_session_id'), 'interview_feedbacks', ['session_id'], unique=False)

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('encrypted_data', sa.LargeBinary(), nullable=False),
        sa.Column('salt', sa.LargeBinary(length=16), nullable=False),
        sa.Column('nonce', sa.LargeBinary(length=12), nullable=False),
        sa.Column('tag', sa.LargeBinary(length=16), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_accessed', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_category'), 'documents', ['category'], unique=False)
    op.create_index(op.f('ix_documents_document_id'), 'documents', ['document_id'], unique=True)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    op.create_index('idx_user_document', 'documents', ['user_id', 'document_id'], unique=False)
    op.create_index('idx_user_category', 'documents', ['user_id', 'category'], unique=False)
    op.create_index('idx_upload_date', 'documents', ['upload_date'], unique=False)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('module_type', sa.String(length=50), nullable=False),
        sa.Column('messages_json', sa.JSON(), nullable=True),
        sa.Column('conversation_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_module_type'), 'conversations', ['module_type'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # Create rate_limit_logs table
    op.create_table(
        'rate_limit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rate_limit_logs_ip_address'), 'rate_limit_logs', ['ip_address'], unique=False)
    op.create_index(op.f('ix_rate_limit_logs_timestamp'), 'rate_limit_logs', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_table('rate_limit_logs')
    op.drop_table('conversations')
    op.drop_table('documents')
    op.drop_table('interview_feedbacks')
    op.drop_table('interview_sessions')
    op.drop_table('welfare_schemes')
    op.drop_table('internship_jobs')
    op.drop_table('users')
