import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import sublime
import sublime_plugin

_server = None
_lock = threading.Lock()

DEFAULT_TEMPLATE = """\
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    return 0;
}
"""


def _settings():
    return sublime.load_settings("CompetitiveCompanionFOC.sublime-settings")


def _sol_path():
    return os.path.expanduser(_settings().get("sol_path", "~/cp/sol.cpp"))


def _template():
    tp = _settings().get("template_path", "")
    if tp:
        tp = os.path.expanduser(tp)
        if os.path.exists(tp):
            with open(tp) as f:
                return f.read()
    return DEFAULT_TEMPLATE


def _port():
    return _settings().get("port", 10045)


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length))
        self.send_response(200)
        self.end_headers()
        sublime.set_timeout(lambda: _on_problem(data), 0)

    def log_message(self, *_):
        pass


def _on_problem(data):
    sol = _sol_path()

    with open(sol, "w") as f:
        f.write(_template())

    tests = data.get("tests", [])
    with open(sol + ":tests", "w") as f:
        json.dump([{"test": t["input"]} for t in tests], f, indent=2)

    window = sublime.active_window()
    view = window.open_file(sol)
    name = data.get("name", "problem")
    sublime.status_message(f"CC: {name} ({len(tests)} tests)")

    if not _settings().get("auto_run_foc", True):
        return

    def _run_foc():
        if view.is_loading():
            sublime.set_timeout(_run_foc, 100)
            return
        window.focus_view(view)
        view.run_command("view_tester", {"action": "make_opd", "use_debugger": False})

    sublime.set_timeout(_run_foc, 200)


def _start():
    global _server
    with _lock:
        if _server is not None:
            return False
        try:
            _server = HTTPServer(("", _port()), _Handler)
        except OSError as e:
            sublime.error_message(f"CompetitiveCompanionFOC: could not bind port {_port()}\n{e}")
            return False
        t = threading.Thread(target=_server.serve_forever, daemon=True)
        t.start()
        return True


def _stop():
    global _server
    with _lock:
        if _server is None:
            return False
        _server.shutdown()
        _server = None
        return True


def plugin_loaded():
    if _start():
        sublime.status_message(f"Competitive Companion listening on port {_port()}")


def plugin_unloaded():
    _stop()


# ── Commands ─────────────────────────────────────────────────────────────────

class CcStartListenerCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        if _start():
            sublime.status_message(f"CC listener started on port {_port()}")
        else:
            sublime.status_message("CC listener is already running")

    def is_enabled(self):
        return _server is None


class CcStopListenerCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        if _stop():
            sublime.status_message("CC listener stopped")
        else:
            sublime.status_message("CC listener is not running")

    def is_enabled(self):
        return _server is not None


class CcRestartListenerCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        _stop()
        if _start():
            sublime.status_message(f"CC listener restarted on port {_port()}")


class CcStatusCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        if _server is not None:
            sublime.message_dialog(f"Competitive Companion listener is RUNNING on port {_port()}")
        else:
            sublime.message_dialog("Competitive Companion listener is STOPPED")
