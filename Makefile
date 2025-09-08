# Testing commands
test-health:
	uv run python examples/health_check.py

test-endpoints:
	uv run python examples/test_endpoints.py

test-integration:
	uv run python examples/integration_test.py

test-load:
	uv run python examples/load_test.py

test-all: test-health test-endpoints
	@echo "All endpoint tests completed"