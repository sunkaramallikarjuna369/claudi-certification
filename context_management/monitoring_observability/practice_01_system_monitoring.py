"""
PRACTICE 01: MONITORING & OBSERVABILITY
=======================================

Monitoring Concepts:
- Track system health and performance
- Monitor error rates and latency
- Observe cost and resource usage
- Configure alerts for anomalies
- Build dashboards for visibility

Key Areas:
1. System health monitoring
2. Performance metrics tracking
3. Error rate tracking
4. Latency monitoring
5. Cost monitoring
6. Alert configuration
7. Dashboard design
"""

import os
import time
from datetime import datetime, timedelta
from collections import defaultdict
from anthropic import Anthropic

# =============================================================================
# SETUP: Load environment and initialize client
# =============================================================================

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            if 'ANTHROPIC_API_KEY' in line and '=' in line:
                key_value = line.split('=', 1)[1].strip()
                if key_value and not key_value.startswith('#'):
                    os.environ['ANTHROPIC_API_KEY'] = key_value

client = Anthropic()
MODEL = "claude-haiku-4-5-20250601"


# =============================================================================
# SCENARIO 1: Basic Metrics Collector
# =============================================================================

class MetricsCollector:
    """
    METRICS COLLECTOR: Track key performance indicators

    Interview Q: What metrics should you monitor for LLM APIs?
    A: Request count, latency, error rate, token usage, cost,
       cache hit rate, and model-specific metrics.

    BEST PRACTICE: Collect metrics at every request for visibility
    """

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.latencies = []  # For percentile calculations
        self.errors_by_type = defaultdict(int)

    def record_request(self, latency, input_tokens, output_tokens, success=True, error_type=None):
        """Record metrics for a request"""
        self.request_count += 1
        self.total_latency += latency
        self.latencies.append(latency)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        if not success:
            self.error_count += 1
            if error_type:
                self.errors_by_type[error_type] += 1

    def get_metrics(self):
        """Get current metrics"""
        avg_latency = self.total_latency / self.request_count if self.request_count > 0 else 0

        # Calculate percentile
        sorted_latencies = sorted(self.latencies) if self.latencies else [0]
        p50_idx = int(len(sorted_latencies) * 0.5)
        p95_idx = int(len(sorted_latencies) * 0.95)
        p99_idx = int(len(sorted_latencies) * 0.99)

        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "avg_latency_ms": avg_latency * 1000,
            "p50_latency_ms": sorted_latencies[p50_idx] * 1000 if sorted_latencies else 0,
            "p95_latency_ms": sorted_latencies[p95_idx] * 1000 if len(sorted_latencies) > p95_idx else 0,
            "p99_latency_ms": sorted_latencies[p99_idx] * 1000 if len(sorted_latencies) > p99_idx else 0,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "errors_by_type": dict(self.errors_by_type)
        }

    def reset(self):
        """Reset all metrics"""
        self.__init__()


def demonstrate_metrics_collector():
    """Show metrics collector in action"""
    print("=" * 60)
    print("SCENARIO 1: Basic Metrics Collector")
    print("=" * 60)

    collector = MetricsCollector()

    # Simulate requests with varying latencies
    print("Recording simulated requests:")
    test_data = [
        (0.1, 100, 50, True, None),
        (0.2, 150, 75, True, None),
        (0.15, 120, 60, True, None),
        (0.5, 200, 100, False, "rate_limit"),
        (0.1, 100, 50, True, None),
    ]

    for latency, in_tok, out_tok, success, err_type in test_data:
        collector.record_request(latency, in_tok, out_tok, success, err_type)
        status = "OK" if success else f"Error: {err_type}"
        print(f"  Latency: {latency*1000:.0f}ms, Tokens: {in_tok+out_tok}, Status: {status}")

    metrics = collector.get_metrics()
    print(f"\nMetrics Summary:")
    print(f"  Total requests: {metrics['request_count']}")
    print(f"  Errors: {metrics['error_count']} ({metrics['error_rate']:.1f}%)")
    print(f"  Avg latency: {metrics['avg_latency_ms']:.1f}ms")
    print(f"  P95 latency: {metrics['p95_latency_ms']:.1f}ms")
    print(f"  Total tokens: {metrics['total_tokens']}")
    print(f"  Errors by type: {metrics['errors_by_type']}")
    print()


# =============================================================================
# SCENARIO 2: Latency Monitoring
# =============================================================================

class LatencyMonitor:
    """
    LATENCY MONITOR: Track and alert on latency issues

    Interview Q: How do you monitor API latency?
    A: Track latency per request, calculate percentiles (p50, p95, p99),
       alert if latency exceeds thresholds.

    BEST PRACTICE: Use histograms for accurate percentile calculation
    """

    def __init__(self, warning_threshold=1.0, critical_threshold=3.0):
        self.warning_threshold = warning_threshold  # seconds
        self.critical_threshold = critical_threshold
        self.samples = []
        self.alerts = []

    def record(self, latency_seconds):
        """Record a latency sample"""
        self.samples.append({
            "latency": latency_seconds,
            "timestamp": datetime.now()
        })

        # Check thresholds
        if latency_seconds > self.critical_threshold:
            self.alerts.append({
                "level": "CRITICAL",
                "latency": latency_seconds,
                "time": datetime.now()
            })
        elif latency_seconds > self.warning_threshold:
            self.alerts.append({
                "level": "WARNING",
                "latency": latency_seconds,
                "time": datetime.now()
            })

        # Keep only last 1000 samples
        self.samples = self.samples[-1000:]

    def get_stats(self):
        """Get latency statistics"""
        if not self.samples:
            return {"count": 0}

        latencies = sorted([s["latency"] for s in self.samples])
        count = len(latencies)

        return {
            "count": count,
            "avg": sum(latencies) / count,
            "min": min(latencies),
            "max": max(latencies),
            "p50": latencies[int(count * 0.5)],
            "p95": latencies[int(count * 0.95)] if count > 20 else None,
            "p99": latencies[int(count * 0.99)] if count > 100 else None,
        }

    def get_recent_alerts(self, count=10):
        """Get recent alerts"""
        return self.alerts[-count:]


def demonstrate_latency_monitor():
    """Show latency monitoring"""
    print("=" * 60)
    print("SCENARIO 2: Latency Monitoring")
    print("=" * 60)

    monitor = LatencyMonitor(warning_threshold=0.5, critical_threshold=1.0)

    # Simulate varying latencies
    latencies = [0.1, 0.2, 0.3, 0.15, 0.8, 1.2, 0.2, 0.1, 0.5, 0.3]
    print("Recording latencies:")
    for lat in latencies:
        monitor.record(lat)
        alert_marker = ""
        if lat > 1.0:
            alert_marker = " [CRITICAL]"
        elif lat > 0.5:
            alert_marker = " [WARNING]"
        print(f"  {lat:.1f}s{alert_marker}")

    stats = monitor.get_stats()
    print(f"\nLatency Stats:")
    print(f"  Count: {stats['count']}")
    print(f"  Avg: {stats['avg']*1000:.1f}ms")
    print(f"  Min: {stats['min']*1000:.1f}ms")
    print(f"  Max: {stats['max']*1000:.1f}ms")
    print(f"  P50: {stats['p50']*1000:.1f}ms")
    print(f"  P95: {stats['p95']*1000:.1f}ms" if stats['p95'] else "  P95: N/A")

    alerts = monitor.get_recent_alerts()
    if alerts:
        print(f"\nRecent Alerts: {len(alerts)}")
        for a in alerts:
            print(f"  {a['level']}: {a['latency']*1000:.0f}ms at {a['time']}")
    print()


# =============================================================================
# SCENARIO 3: Error Rate Tracking
# =============================================================================

class ErrorRateTracker:
    """
    ERROR RATE TRACKER: Monitor error patterns and trends

    Interview Q: How do you track error rates?
    A: Count errors vs total requests over time windows.
       Track error types for debugging. Alert on spikes.

    BEST PRACTICE: Track both rate and count, and error types
    """

    def __init__(self, warning_rate=5.0, critical_rate=10.0):
        self.warning_rate = warning_rate  # percent
        self.critical_rate = critical_rate
        self.errors = []
        self.total_requests = 0

    def record(self, success, error_type=None):
        """Record request result"""
        self.total_requests += 1
        if not success:
            self.errors.append({
                "type": error_type or "unknown",
                "timestamp": datetime.now()
            })

    def get_error_rate(self, window_minutes=5):
        """Calculate error rate for time window"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=window_minutes)

        recent_errors = [e for e in self.errors if e["timestamp"] > cutoff]
        recent_total = min(self.total_requests, window_minutes * 20)  # Approx

        if recent_total == 0:
            return 0.0

        return (len(recent_errors) / recent_total) * 100

    def get_error_breakdown(self):
        """Get breakdown of errors by type"""
        breakdown = defaultdict(int)
        for e in self.errors:
            breakdown[e["type"]] += 1
        return dict(breakdown)

    def check_thresholds(self):
        """Check if error rate exceeds thresholds"""
        rate = self.get_error_rate()
        if rate >= self.critical_rate:
            return "CRITICAL", rate
        elif rate >= self.warning_rate:
            return "WARNING", rate
        return "OK", rate


def demonstrate_error_tracker():
    """Show error rate tracking"""
    print("=" * 60)
    print("SCENARIO 3: Error Rate Tracking")
    print("=" * 60)

    tracker = ErrorRateTracker(warning_rate=5.0, critical_rate=10.0)

    # Simulate requests with some errors
    print("Recording requests (1=success, 0=error):")
    results = [1, 1, 1, 0, 1, 0, 1, 1, 0, 1]
    error_types = [None, None, None, "rate_limit", None, "timeout", None, None, "auth", None]

    for i, (result, err_type) in enumerate(zip(results, error_types)):
        tracker.record(success=(result == 1), error_type=err_type)
        status = "OK" if result == 1 else f"Error: {err_type}"
        print(f"  Request {i+1}: {status}")

    status, rate = tracker.check_thresholds()
    print(f"\nError Rate Status: {status} ({rate:.1f}%)")
    print(f"Total requests: {tracker.total_requests}")
    print(f"Total errors: {len(tracker.errors)}")
    print(f"Error breakdown: {tracker.get_error_breakdown()}")
    print()


# =============================================================================
# SCENARIO 4: Cost Monitoring
# =============================================================================

class CostMonitor:
    """
    COST MONITOR: Track API spending in real-time

    Interview Q: How do you monitor API costs?
    A: Track tokens used and multiply by cost per token.
       Monitor daily/monthly spending vs budget. Alert on trends.

    BEST PRACTICE: Track by time period, model, and operation type
    """

    # Cost per token (example rates)
    INPUT_COST_PER_1K = 0.000025  # $0.000025 per input token
    OUTPUT_COST_PER_1K = 0.000125  # $0.000125 per output token

    def __init__(self, daily_budget=50.0, warning_percent=80):
        self.daily_budget = daily_budget
        self.warning_percent = warning_percent
        self.hourly_spending = defaultdict(float)
        self.daily_spending = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def record_tokens(self, input_tokens, output_tokens):
        """Record token usage and calculate cost"""
        input_cost = (input_tokens / 1000) * self.INPUT_COST_PER_1K
        output_cost = (output_tokens / 1000) * self.OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.daily_spending += total_cost

        hour = datetime.now().strftime("%H:00")
        self.hourly_spending[hour] += total_cost

        return total_cost

    def get_stats(self):
        """Get spending statistics"""
        remaining = self.daily_budget - self.daily_spending
        used_percent = (self.daily_spending / self.daily_budget) * 100

        return {
            "daily_spent": self.daily_spending,
            "daily_budget": self.daily_budget,
            "remaining": remaining,
            "used_percent": used_percent,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "hourly_spending": dict(self.hourly_spending)
        }

    def check_budget(self):
        """Check if within budget"""
        used_percent = (self.daily_spending / self.daily_budget) * 100

        if self.daily_spending >= self.daily_budget:
            return "EXHAUSTED", used_percent
        elif used_percent >= self.warning_percent:
            return "WARNING", used_percent
        return "OK", used_percent


def demonstrate_cost_monitor():
    """Show cost monitoring"""
    print("=" * 60)
    print("SCENARIO 4: Cost Monitoring")
    print("=" * 60)

    monitor = CostMonitor(daily_budget=10.00, warning_percent=80)

    print("Recording token usage:")
    usage = [
        (1000, 500),  # Request 1
        (1500, 750),  # Request 2
        (2000, 1000), # Request 3
    ]

    for i, (in_tok, out_tok) in enumerate(usage):
        cost = monitor.record_tokens(in_tok, out_tok)
        print(f"  Request {i+1}: {in_tok + out_tok} tokens, ${cost:.6f}")

    stats = monitor.get_stats()
    print(f"\nCost Stats:")
    print(f"  Daily spent: ${stats['daily_spent']:.4f}")
    print(f"  Daily budget: ${stats['daily_budget']:.2f}")
    print(f"  Remaining: ${stats['remaining']:.4f}")
    print(f"  Usage: {stats['used_percent']:.1f}%")
    print(f"  Total tokens: {stats['total_tokens']:,}")

    status, percent = monitor.check_budget()
    print(f"\nBudget Status: {status} ({percent:.1f}% used)")
    print()


# =============================================================================
# SCENARIO 5: Dashboard Design
# =============================================================================

def demonstrate_dashboard():
    """
    REAL-TIME SCENARIO: Building monitoring dashboard

    BEST PRACTICE: Key dashboard metrics to display:
    - Request rate (requests/minute)
    - Error rate (%)
    - Latency (avg, p95)
    - Cost ($/hour)
    - Cache hit rate (%)

    Interview Q: What metrics should be on a monitoring dashboard?
    A: Request throughput, error rate, latency percentiles,
       cost per hour, and cache hit rate.
    """
    print("=" * 60)
    print("SCENARIO 5: Dashboard Design")
    print("=" * 60)

    # Simulate dashboard data
    dashboard_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_health": {
            "status": "HEALTHY",
            "uptime_percent": 99.5,
        },
        "requests": {
            "total_today": 1547,
            "per_minute": 12.5,
        },
        "latency": {
            "avg_ms": 250,
            "p50_ms": 200,
            "p95_ms": 850,
            "p99_ms": 1200,
        },
        "errors": {
            "count_today": 23,
            "rate_percent": 1.5,
            "top_type": "rate_limit",
        },
        "cost": {
            "spent_today": 8.45,
            "daily_budget": 50.00,
            "hourly_rate": 0.35,
        },
        "cache": {
            "hit_rate": 78.5,
            "hits": 1215,
            "misses": 332,
        }
    }

    print("+--------------------------------------------------+")
    print("|         MONITORING DASHBOARD                      |")
    print("+--------------------------------------------------+")
    print(f"| Updated: {dashboard_data['timestamp']:<33} |")
    print("+--------------------------------------------------+")
    print("| SYSTEM HEALTH: {:<35} |".format(dashboard_data['system_health']['status']))
    print("| Uptime: {:.1f}%{:<30} |".format(dashboard_data['system_health']['uptime_percent'], ""))
    print("+--------------------------------------------------+")
    print("| REQUESTS                                          |")
    print("|   Total today: {:>6}{:<28} |".format(dashboard_data['requests']['total_today'], ""))
    print("|   Rate: {:>6.1f}/min{:<26} |".format(dashboard_data['requests']['per_minute'], ""))
    print("+--------------------------------------------------+")
    print("| LATENCY                                           |")
    print("|   Average: {:>6}ms{:<27} |".format(dashboard_data['latency']['avg_ms'], ""))
    print("|   P95: {:>6}ms{:<29} |".format(dashboard_data['latency']['p95_ms'], ""))
    print("|   P99: {:>6}ms{:<29} |".format(dashboard_data['latency']['p99_ms'], ""))
    print("+--------------------------------------------------+")
    print("| ERRORS                                            |")
    print("|   Count today: {:>6}{:<27} |".format(dashboard_data['errors']['count_today'], ""))
    print("|   Rate: {:>6.1f}%{:<30} |".format(dashboard_data['errors']['rate_percent'], ""))
    print("+--------------------------------------------------+")
    print("| COST                                              |")
    print("|   Spent today: ${:>6.2f} / ${:>5.2f}{:<12} |".format(
        dashboard_data['cost']['spent_today'],
        dashboard_data['cost']['daily_budget'],
        ""
    ))
    print("|   Hourly rate: ${:>5.2f}{:<26} |".format(dashboard_data['cost']['hourly_rate'], ""))
    print("+--------------------------------------------------+")
    print("| CACHE                                             |")
    print("|   Hit rate: {:>6.1f}%{:<27} |".format(dashboard_data['cache']['hit_rate'], ""))
    print("|   Hits: {:>6} / Misses: {:>5}{:<16} |".format(
        dashboard_data['cache']['hits'],
        dashboard_data['cache']['misses'],
        ""
    ))
    print("+--------------------------------------------------+")
    print()


# =============================================================================
# SCENARIO 6: Alert Configuration
# =============================================================================

class AlertManager:
    """
    ALERT MANAGER: Configure and trigger alerts

    Interview Q: How do you configure alerts?
    A: Set thresholds for key metrics. When threshold exceeded,
       trigger alert with severity level. Include context.

    BEST PRACTICE: Multiple severity levels (INFO, WARNING, CRITICAL)
    """

    def __init__(self):
        self.alerts = []
        self.thresholds = {
            "latency_p95": {"warning": 1000, "critical": 2000},
            "error_rate": {"warning": 5, "critical": 10},
            "cost_percent": {"warning": 80, "critical": 95},
        }

    def check_and_alert(self, metric, value):
        """Check metric against thresholds, create alert if needed"""
        if metric not in self.thresholds:
            return None

        threshold = self.thresholds[metric]
        if value >= threshold["critical"]:
            alert = {"severity": "CRITICAL", "metric": metric, "value": value}
            self.alerts.append(alert)
            return alert
        elif value >= threshold["warning"]:
            alert = {"severity": "WARNING", "metric": metric, "value": value}
            self.alerts.append(alert)
            return alert
        return None

    def get_active_alerts(self):
        """Get recent active alerts"""
        return self.alerts[-10:]

    def clear_alerts(self):
        """Clear alert history"""
        self.alerts = []


def demonstrate_alert_manager():
    """Show alert configuration"""
    print("=" * 60)
    print("SCENARIO 6: Alert Configuration")
    print("=" * 60)

    manager = AlertManager()

    print("Checking metrics against thresholds:")
    checks = [
        ("latency_p95", 850, "OK"),
        ("latency_p95", 1100, "WARNING"),
        ("latency_p95", 2500, "CRITICAL"),
        ("error_rate", 3, "OK"),
        ("error_rate", 7, "WARNING"),
        ("cost_percent", 82, "WARNING"),
    ]

    for metric, value, expected in checks:
        result = manager.check_and_alert(metric, value)
        status = result["severity"] if result else "OK"
        marker = "[OK]" if status == expected else f"[{status}!]"
        print(f"  {metric}={value}: {status} {marker}")

    print(f"\nActive alerts: {len(manager.alerts)}")
    for alert in manager.get_active_alerts():
        print(f"  {alert['severity']}: {alert['metric']}={alert['value']}")
    print()


# =============================================================================
# SCENARIO 7: Real API Monitoring
# =============================================================================

def demonstrate_real_api_monitoring():
    """Show monitoring with real API call"""
    print("=" * 60)
    print("SCENARIO 7: Real API Monitoring")
    print("=" * 60)

    collector = MetricsCollector()
    cost_monitor = CostMonitor(daily_budget=10.00)

    try:
        print("Making monitored API call...")
        start_time = time.time()

        response = client.messages.create(
            model=MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": "Say 'test'"}]
        )

        latency = time.time() - start_time

        # Record metrics
        input_tok = response.usage.input_tokens
        output_tok = response.usage.output_tokens
        collector.record_request(latency, input_tok, output_tok, success=True)
        cost_monitor.record_tokens(input_tok, output_tok)

        print(f"Request completed!")
        print(f"  Latency: {latency*1000:.1f}ms")
        print(f"  Input tokens: {input_tok}")
        print(f"  Output tokens: {output_tok}")

        metrics = collector.get_metrics()
        cost_stats = cost_monitor.get_stats()

        print(f"\nMonitored Metrics:")
        print(f"  Total requests: {metrics['request_count']}")
        print(f"  Avg latency: {metrics['avg_latency_ms']:.1f}ms")
        print(f"  Total cost: ${cost_stats['daily_spent']:.6f}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    print()


# =============================================================================
# MAIN: Run All Scenarios
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MONITORING & OBSERVABILITY - PRACTICE FILE")
    print("=" * 60 + "\n")

    demonstrate_metrics_collector()
    demonstrate_latency_monitor()
    demonstrate_error_tracker()
    demonstrate_cost_monitor()
    demonstrate_dashboard()
    demonstrate_alert_manager()
    demonstrate_real_api_monitoring()

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT")
    print("=" * 60)
    print("""
1. METRICS COLLECTION
   - Track request count, latency, errors, tokens
   - Calculate percentiles (p50, p95, p99)
   - Record for later analysis

2. LATENCY MONITORING
   - Track latency per request
   - Alert on threshold breaches
   - Use histograms for percentile accuracy

3. ERROR RATE TRACKING
   - Count errors vs total requests
   - Track error types for debugging
   - Alert on spikes (5%, 10% thresholds)

4. COST MONITORING
   - Track tokens and multiply by rate
   - Monitor daily spending vs budget
   - Alert when approaching limits

5. DASHBOARD DESIGN
   - Display key metrics: throughput, latency, errors, cost
   - Include both current values and trends
   - Use clear visual indicators

6. ALERT CONFIGURATION
   - Set thresholds for each metric
   - Multiple severity levels (WARNING, CRITICAL)
   - Include context in alerts

7. OBSERVABILITY PRINCIPLES
   - You can't improve what you don't measure
   - Monitor everything that matters
   - Alerts should be actionable

INTERVIEW QUESTIONS & ANSWERS:
------------------------------
Q: What metrics should you monitor for LLM APIs?
A: Request throughput, latency (p50, p95, p99), error rate,
   token usage, cost per hour, and cache hit rate.

Q: How do you track error rates?
A: Count errors vs total requests over time windows.
   Track error types for debugging. Alert on spikes.

Q: What should be on a monitoring dashboard?
A: Request throughput, error rate, latency percentiles,
   cost per hour, and cache hit rate.

Q: How do you configure alerts?
A: Set thresholds for key metrics. When exceeded,
   trigger alert with severity level and context.
""")