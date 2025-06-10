import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Base and all models
from database.connection import Base, get_sync_database_url
from config.settings import get_settings

# CRITICAL: Import ALL models for autogenerate detection
from database.models import *

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    """Get database URL from environment variables."""
    db_url = get_sync_database_url()
    return db_url

def include_name(name, type_, parent_names):
    """
    Should this name be included in autogenerate?
    This controls which schemas are included.
    """
    if type_ == "schema":
        # Include both public and carbonleap schemas
        return name in [None, "public", "carbonleap"]
    return True

def include_object(object, name, type_, reflected, compare_to):
    """
    Should this object be included in autogenerate?
    Return True to include, False to exclude.
    """
    # Exclude PostGIS and other system tables
    exclude_tables = [
        # PostGIS tables
        "spatial_ref_sys",
        "geography_columns", 
        "geometry_columns",
        "raster_columns",
        "raster_overviews",
        
        # Django tables - exclude all existing Django/legacy tables
        "app_registry",
        "django_session",
        "user_preference", 
        "features",
        "subscription_details",
        "user_role_dataspace_mapping",
        "role_permission_mapping",
        "user_audit",
        "auth_group_permissions",
        "deletion_audit_log",
        "prompts",
        "auth_group",
        "django_content_type",
        "app_client",
        "auth_user",
        "auth_user_user_permissions",
        "role",
        "app_domain",
        "app_provisioning",
        "application_metadata",
        "dataspace",
        "auth_permission",
        "user_schema_version",
        "auth_user_groups",
        "django_migrations",
        "role_permission_mapping_audit",
        "role_audit",
        "subscription_limit",
        "api_identifier",
        "django_admin_log",
        "permissions",  # From the sequence detection
        "users",        # From the sequence detection
        "roles",
        "user_roles",
        "role_permissions"
    ]
    
    # Exclude Django/legacy tables and their indexes
    if type_ == "table" and name in exclude_tables:
        return False
        
    # Exclude indexes on excluded tables
    if type_ == "index":
        # Get table name from index (this is a simplified approach)
        for excluded_table in exclude_tables:
            if excluded_table in name.lower():
                return False
    
    # Include everything else (your new models)
    return True

def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """
    Compare types for autogenerate.
    Return True if they're different, False if they're the same.
    """
    # Handle UUID type comparison
    if hasattr(metadata_type, 'impl') and hasattr(inspected_type, 'impl'):
        if str(metadata_type.impl) == str(inspected_type.impl):
            return False
    
    # Default comparison
    return context.impl.compare_type(inspected_column, metadata_column)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        url = get_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        include_name=include_name,
        compare_type=compare_type,
        include_schemas=True,
        version_table_schema="carbonleap", # Put version table in carbonleap schema
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    
    # Override with environment URL if not set
    if not configuration.get("sqlalchemy.url"):
        configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            include_name=include_name,
            compare_type=compare_type,
            compare_server_default=True,
            render_as_batch=False,
            include_schemas=True,
            version_table_schema="carbonleap",  # Put version table in carbonleap schema
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()