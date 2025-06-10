.PHONY: test-job-discovery test-quick test-docker test-api test-flows help

# Default target
help:
	@echo "Job Discovery Pipeline Test Commands:"
	@echo "  make test-job-discovery  - Run full job discovery pipeline test"
	@echo "  make test-quick         - Run quick pipeline test"
	@echo "  make test-docker        - Run tests in Docker environment"
	@echo "  make test-api           - Test API endpoints (requires running server)"
	@echo "  make test-flows         - Run all flow tests"
	@echo "  make setup              - Set up test environment"

setup:
	@echo "🔧 Setting up test environment..."
	python3 -m venv env
	source env/bin/activate && pip install -r app/requirements.txt
	@echo "✅ Setup complete"

test-job-discovery:
	@echo "🧪 Running Job Discovery Pipeline tests..."
	bash scripts/quick_test_job_discovery.sh

test-quick:
	@echo "⚡ Running quick pipeline test..."
	python3 playground/job_discovery_pipeline.py

test-docker:
	@echo "🐳 Running Docker tests..."
	bash scripts/test_job_discovery_docker.sh

test-api:
	@echo "🌐 Testing API endpoints..."
	bash scripts/test_job_discovery_pipeline.sh

test-flows:
	@echo "🔄 Running all flow tests..."
	bash scripts/test_job_discovery_flows.sh

test-all: test-job-discovery test-api
	@echo "🎉 All tests complete"