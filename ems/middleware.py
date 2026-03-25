"""
Middleware for GET response caching.
Caches 200 GET responses per (path, query, user).
Invalidates cache immediately on POST/PUT/PATCH/DELETE (2xx) so next GET returns fresh data.
"""
from django.utils.deprecation import MiddlewareMixin
from .cache_utils import (
    get_cached_response,
    set_cached_response,
    get_cache_key_for_request,
    invalidate_get_cache_for_prefix,
    invalidate_get_cache_for_prefix_all_users,
    get_path_prefixes_from_request,
    GLOBAL_INVALIDATE_GET_PREFIXES,
)

# Do not cache these path prefixes (admin, static, notifications GETs, logout, etc.)
CACHE_SKIP_PREFIXES = ("/admin/", "/static/", "/media/", "/notifications/", "/accounts/logout/")
MUTATION_METHODS = ("POST", "PUT", "PATCH", "DELETE")


class CacheGetMiddleware(MiddlewareMixin):
    """
    Cache GET responses and serve from cache when available.
    On POST/PUT/PATCH/DELETE success (2xx), invalidate GET cache for that path so next GET is fresh.
    Add after AuthenticationMiddleware so request.user is set.
    """

    def process_request(self, request):
        if request.method != "GET":
            return None
        if request.path.startswith(CACHE_SKIP_PREFIXES):
            return None
        cached = get_cached_response(request)
        if cached is not None:
            return cached
        request._cache_key = get_cache_key_for_request(request)
        return None

    def process_response(self, request, response):
        if request.path.startswith(CACHE_SKIP_PREFIXES):
            return response
        # Invalidate GET cache on mutation: per-user for most endpoints; all users for GLOBAL_INVALIDATE_GET_PREFIXES (e.g. alerts GET open to all)
        if request.method in MUTATION_METHODS and 200 <= response.status_code < 300:
            user_id = getattr(request.user, "pk", None) if getattr(request.user, "is_authenticated", False) else None
            for prefix in get_path_prefixes_from_request(request):
                if prefix in GLOBAL_INVALIDATE_GET_PREFIXES:
                    invalidate_get_cache_for_prefix_all_users(prefix)
                else:
                    invalidate_get_cache_for_prefix(prefix, user_id=user_id)
        if request.method == "GET" and getattr(request, "_cache_key", None) is not None and response.status_code == 200:
            set_cached_response(request, response)
        return response


# =============================================================================
# Prometheus HTTP Middleware
# =============================================================================
import time
from prometheus_client import Counter, Histogram, Gauge

_HTTP_REQUESTS_TOTAL = Counter(
    "django_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
_HTTP_DURATION_SECONDS = Histogram(
    "django_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)
_HTTP_IN_PROGRESS = Gauge(
    "django_http_requests_in_progress",
    "In-flight HTTP requests",
    ["method"],
)


def _norm(path: str) -> str:
    return "/".join("<id>" if p.isdigit() else p for p in path.split("/"))


class PrometheusMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == "/metrics":
            return None
        request._prom_t = time.perf_counter()
        _HTTP_IN_PROGRESS.labels(method=request.method).inc()

    def process_response(self, request, response):
        if request.path == "/metrics":
            return response
        t = getattr(request, "_prom_t", None)
        if t is None:
            return response
        path = _norm(request.path)
        _HTTP_REQUESTS_TOTAL.labels(method=request.method, path=path, status=str(response.status_code)).inc()
        _HTTP_DURATION_SECONDS.labels(method=request.method, path=path).observe(time.perf_counter() - t)
        _HTTP_IN_PROGRESS.labels(method=request.method).dec()
        return response
