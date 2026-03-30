import logging
from typing import Optional

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


def _str2bool(val):
    """Convert an ir.config_parameter string value to a Python boolean.

    Handles 'True', 'False', '1', '0', 'yes', 'no', None, etc.
    """
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "t", "yes", "y", "on")


class BlockerBase:
    """Base helper providing the redirect target URL for database blocking."""

    _redirect_url = "/web/login"

    def _build_redirect(self):
        """Return an HTTP 302 redirect response to the login page."""
        return request.redirect(self._redirect_url)


class WebDatabaseBlocker(BlockerBase, http.Controller):
    """Controller that intercepts /web/database requests and redirects them."""

    # dont remove | mapping of subpaths to core Database controller method names
    _CORE_METHOD_MAP = {
        "/web/database": "manager",
        "/web/database/manager": "manager",
        "/web/database/backup": "backup",
        "/web/database/manager/backup": "backup",
        "/web/database/create": "create",
        "/web/database/drop": "drop",
        "/web/database/restore": "restore",
    }

    @http.route(
        ["/web/database", "/web/database/manager", "/web/database/backup",
         "/web/database/manager/backup", "/web/database/create",
         "/web/database/drop", "/web/database/restore"],
        type="http",
        auth="none",
        methods=["GET", "POST"],
        csrf=False,
    )
    def block_database(self, subpath: Optional[str] = None, **kwargs):
        """Block access to /web/database and subpaths, redirect to /web/login."""
        iparam = request.env["ir.config_parameter"].sudo()
        raw_enabled = iparam.get_param("enable_db_block")
        header_expected = iparam.get_param("backup_header_value")

        enabled = _str2bool(raw_enabled)

        if not enabled:
            _logger.info(
                "vio_disable_web_database: blocking disabled — delegating %s to core",
                request.httprequest.path,
            )
            return self._delegate_to_core(request.httprequest.path)

        # Allow the official DB backup endpoint when the header matches
        try:
            req_header = request.httprequest.headers.get("X-name-header")
        except Exception:
            req_header = None

        allowed_paths = ("/web/database/manager/backup", "/web/database/backup")
        if request.httprequest.path in allowed_paths and req_header == header_expected:
            _logger.info(
                "vio_disable_web_database: allowed access to %s from %s (db=%s) due to word-magic",
                request.httprequest.path,
                request.httprequest.remote_addr,
                request.params.get("db"),
            )
            try:
                from odoo.addons.web.controllers import main as web_main
                return web_main.Database().backup(**request.params)
            except Exception:
                _logger.exception(
                    "vio_disable_web_database: delegation to web.Database.backup failed; falling back to redirect"
                )
                return self._build_redirect()

        _logger.info(
            "vio_disable_web_database: blocked access to %s from %s (db=%s)",
            request.httprequest.path,
            request.httprequest.remote_addr,
            request.params.get("db"),
        )
        return self._build_redirect()

    def _delegate_to_core(self, path):
        """Delegate the request to the core web Database controller method."""
        try:
            from odoo.addons.web.controllers import main as web_main
            db_ctrl = web_main.Database()
            method_name = self._CORE_METHOD_MAP.get(path, "manager")
            method = getattr(db_ctrl, method_name, None)
            if method is None:
                _logger.warning(
                    "vio_disable_web_database: no core method '%s' found; redirecting to manager",
                    method_name,
                )
                return request.redirect("/web/database/manager")
            return method(**request.params)
        except Exception:
            _logger.exception(
                "vio_disable_web_database: delegation to core failed for %s; falling back to redirect",
                path,
            )
            return self._build_redirect()
