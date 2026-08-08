#!/usr/bin/env python3
"""
Production-Ready Web Application Health & Endpoint Monitoring Tool for freelance_rate_predictor

Features:
- Parallel execution using concurrent.futures.ThreadPoolExecutor
- HTTP status code validation & latency threshold checks
- Cross-platform color-coded terminal reports (via colorama / ANSI)
- CI/CD pipeline integration with non-zero exit codes on failure
"""

import sys
import time
import argparse
from typing import List, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Try importing colorama for cross-platform Windows terminal color support
try:
    import colorama
    colorama.init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


# ==============================================================================
# Terminal Color Formatting Utility
# ==============================================================================
class Colors:
    """ANSI color codes for terminal formatting."""
    GREEN = "\033[92m" if sys.stdout.isatty() or HAS_COLORAMA else ""
    YELLOW = "\033[93m" if sys.stdout.isatty() or HAS_COLORAMA else ""
    RED = "\033[91m" if sys.stdout.isatty() or HAS_COLORAMA else ""
    CYAN = "\033[96m" if sys.stdout.isatty() or HAS_COLORAMA else ""
    BOLD = "\033[1m" if sys.stdout.isatty() or HAS_COLORAMA else ""
    RESET = "\033[0m" if sys.stdout.isatty() or HAS_COLORAMA else ""

    @classmethod
    def disable_colors(cls):
        """Disable color formatting (useful for plain text logging environments)."""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.RED = ""
        cls.CYAN = ""
        cls.BOLD = ""
        cls.RESET = ""


# ==============================================================================
# Data Structures
# ==============================================================================
@dataclass
class Endpoint:
    """Represents an endpoint configuration to test."""
    name: str
    path: str
    expected_status: int = 200
    is_critical: bool = True
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    json_data: Optional[dict] = None


@dataclass
class TestResult:
    """Represents the result of testing a single endpoint."""
    endpoint: Endpoint
    full_url: str
    status_code: Optional[int] = None
    response_time_ms: float = 0.0
    is_up: bool = False
    is_degraded: bool = False
    error_message: Optional[str] = None


# ==============================================================================
# Health Checker Core Class
# ==============================================================================
class AppHealthChecker:
    """Executes parallel health checks across target application endpoints."""

    def __init__(
        self,
        base_url: str,
        endpoints: List[Endpoint],
        timeout: float = 10.0,
        latency_threshold_ms: float = 1000.0,
        max_workers: int = 10
    ):
        self.base_url = base_url.rstrip("/")
        self.endpoints = endpoints
        self.timeout = timeout
        self.latency_threshold_ms = latency_threshold_ms
        self.max_workers = max_workers

    def _check_single_endpoint(self, endpoint: Endpoint) -> TestResult:
        """Ping a single endpoint and validate response status and latency."""
        url = f"{self.base_url}{endpoint.path}"
        result = TestResult(endpoint=endpoint, full_url=url)

        start_time = time.perf_counter()
        try:
            response = requests.request(
                method=endpoint.method,
                url=url,
                headers=endpoint.headers,
                json=endpoint.json_data,
                timeout=self.timeout,
                allow_redirects=True
            )
            elapsed_time_ms = (time.perf_counter() - start_time) * 1000
            result.response_time_ms = round(elapsed_time_ms, 2)
            result.status_code = response.status_code

            # Validate HTTP status code
            if response.status_code == endpoint.expected_status:
                result.is_up = True
                # Check performance threshold
                if result.response_time_ms > self.latency_threshold_ms:
                    result.is_degraded = True
                    result.error_message = (
                        f"Latency ({result.response_time_ms}ms) exceeded "
                        f"threshold ({self.latency_threshold_ms}ms)"
                    )
            else:
                result.is_up = False
                result.error_message = (
                    f"Unexpected HTTP {response.status_code} "
                    f"(expected {endpoint.expected_status})"
                )

        except requests.exceptions.Timeout:
            result.response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            result.is_up = False
            result.error_message = f"Request timed out after {self.timeout}s"
        except requests.exceptions.ConnectionError:
            result.response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            result.is_up = False
            result.error_message = "Connection failed / Server offline"
        except requests.exceptions.RequestException as e:
            result.response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            result.is_up = False
            result.error_message = f"HTTP Error: {type(e).__name__}"

        return result

    def run_checks(self) -> List[TestResult]:
        """Execute checks in parallel using ThreadPoolExecutor."""
        results: List[TestResult] = []
        num_workers = min(self.max_workers, len(self.endpoints))

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_endpoint = {
                executor.submit(self._check_single_endpoint, ep): ep
                for ep in self.endpoints
            }
            for future in as_completed(future_to_endpoint):
                results.append(future.result())

        # Sort results back to match original endpoint order
        endpoint_order = {ep.path: i for i, ep in enumerate(self.endpoints)}
        results.sort(key=lambda r: endpoint_order.get(r.endpoint.path, 0))
        return results


# ==============================================================================
# Reporting & Output Presentation
# ==============================================================================
def print_report(base_url: str, results: List[TestResult], latency_threshold: float) -> bool:
    """Print color-coded summary report and determine overall system health."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*85}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN} FREELANCE RATE PREDICTOR - HEALTH & COMPONENT STATUS REPORT{Colors.RESET}")
    print(f"{Colors.BOLD} Target Host: {base_url}{Colors.RESET}")
    print(f"{Colors.BOLD} Timestamp  : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*85}{Colors.RESET}\n")

    # Table Header
    header = f"{'STATUS':<10} | {'COMPONENT':<24} | {'PATH':<22} | {'HTTP':<5} | {'LATENCY':<9} | {'DETAILS'}"
    print(f"{Colors.BOLD}{header}{Colors.RESET}")
    print("-" * 95)

    any_critical_failed = False
    passed_count = 0
    degraded_count = 0
    failed_count = 0

    for res in results:
        status_code_str = str(res.status_code) if res.status_code is not None else "N/A"
        latency_str = f"{res.response_time_ms:.1f}ms"

        if res.is_up and not res.is_degraded:
            status_tag = f"{Colors.GREEN}[ UP ]{Colors.RESET}"
            details = f"{Colors.GREEN}OK{Colors.RESET}"
            passed_count += 1
        elif res.is_up and res.is_degraded:
            status_tag = f"{Colors.YELLOW}[DEGRADED]{Colors.RESET}"
            details = f"{Colors.YELLOW}{res.error_message}{Colors.RESET}"
            degraded_count += 1
        else:
            status_tag = f"{Colors.RED}[ DOWN ]{Colors.RESET}"
            details = f"{Colors.RED}{res.error_message}{Colors.RESET}"
            failed_count += 1
            if res.endpoint.is_critical:
                any_critical_failed = True

        critical_flag = " *" if res.endpoint.is_critical else ""
        comp_name = f"{res.endpoint.name}{critical_flag}"

        print(
            f"{status_tag:<19} | "
            f"{comp_name:<24} | "
            f"{res.endpoint.path:<22} | "
            f"{status_code_str:<5} | "
            f"{latency_str:<9} | "
            f"{details}"
        )

    print("-" * 95)
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  • Total Endpoints Checked : {len(results)}")
    print(f"  • Healthy ({Colors.GREEN}UP{Colors.RESET})          : {passed_count}")
    print(f"  • High Latency ({Colors.YELLOW}> {latency_threshold}ms{Colors.RESET}) : {degraded_count}")
    print(f"  • Failed ({Colors.RED}DOWN{Colors.RESET})         : {failed_count}")
    print(f"  * Denotes critical components required for pipeline pass.\n")

    if any_critical_failed:
        print(f"{Colors.BOLD}{Colors.RED}>>> RESULT: HEALTH CHECK FAILED - Critical component outage detected.{Colors.RESET}\n")
        return False
    elif failed_count > 0:
        print(f"{Colors.BOLD}{Colors.YELLOW}>>> RESULT: HEALTH CHECK WARNING - Non-critical endpoints failed.{Colors.RESET}\n")
        return True
    else:
        print(f"{Colors.BOLD}{Colors.GREEN}>>> RESULT: HEALTH CHECK PASSED - All components operational.{Colors.RESET}\n")
        return True


# ==============================================================================
# Configuration & CLI Entrypoint
# ==============================================================================
def get_target_endpoints() -> List[Endpoint]:
    """Define endpoints for Freelance Rate Predictor backend & web app."""
    return [
        # Public & Web UI / Docs
        Endpoint(name="Root / API Welcome", path="/", expected_status=200, is_critical=True),
        Endpoint(name="Swagger OpenAPI Docs", path="/docs", expected_status=200, is_critical=False),
        Endpoint(name="ReDoc Documentation", path="/redoc", expected_status=200, is_critical=False),
        Endpoint(name="OpenAPI Schema Spec", path="/openapi.json", expected_status=200, is_critical=True),

        # Backend Health & Database / Model status
        Endpoint(name="Backend Health Check", path="/health", expected_status=200, is_critical=True),

        # ML Prediction Endpoint (POST)
        Endpoint(
            name="ML Predict API (POST)",
            path="/api/v1/predict",
            expected_status=200,
            is_critical=True,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "freelance_sec_demo_key_2026"
            },
            json_data={
                "platform": "Upwork",
                "primary_tech": "Python",
                "project_type": "Custom Development",
                "complexity_level": "Medium",
                "estimated_hours": 40.0,
                "urgency": "Medium",
                "has_auth": 1,
                "has_third_party_apis": 1
            }
        )
    ]


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Parallel Web Application Component Health Checker for Freelance Rate Predictor"
    )
    parser.add_argument(
        "-u", "--base-url",
        default="http://localhost:8000",
        help="Base URL of target web app (e.g. http://localhost:8000 or http://localhost:7860)"
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=1000.0,
        help="Response time warning threshold in milliseconds (default: 1000ms)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout in seconds (default: 10.0s)"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=10,
        help="Maximum parallel threads (default: 10)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output formatting"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.no_color:
        Colors.disable_colors()

    endpoints = get_target_endpoints()
    checker = AppHealthChecker(
        base_url=args.base_url,
        endpoints=endpoints,
        timeout=args.timeout,
        latency_threshold_ms=args.threshold,
        max_workers=args.workers
    )

    results = checker.run_checks()
    is_healthy = print_report(
        base_url=args.base_url,
        results=results,
        latency_threshold=args.threshold
    )

    sys.exit(0 if is_healthy else 1)


if __name__ == "__main__":
    main()
