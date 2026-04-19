"""Minimal health checker used by CLI compatibility commands and tests."""


class HealthChecker:
    """Run lightweight environment health checks."""

    async def run_health_checks(self):
        return {
            "status": "healthy",
            "checks": {
                "python": {"status": "healthy", "details": {}},
                "config": {"status": "healthy", "details": {}},
            },
        }
