## Alembic Commands for Migrations

### Run Migrations
To apply migrations, use the following command:
```bash
alembic upgrade head
```

### Check Current Migration
Check Current Migration Status, use:
```bash
alembic current
```

### Generate a New Migration
To create a new migration script after making changes to your models:
```bash
alembic revision --autogenerate -m "Your migration message"
```

### Downgrade Migration
Downgrade to Previous Migration (if needed):
```bash
alembic downgrade -1  # Go back one migration
# or
alembic downgrade [revision_id]  # Go to specific revision
```

### View Migration History
View Migration History
```
alembic history --verbose
```

### Upgrade to Specific Revision

```
cd app
alembic upgrade [revision_id]
```

### Show SQL Without Applying
```
cd app
alembic upgrade head --sql  # Show SQL for all pending migrations
```
