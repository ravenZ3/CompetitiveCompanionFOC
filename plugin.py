import json
import os
import subprocess
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

import sublime
import sublime_plugin

_server = None
_lock = threading.Lock()

DEFAULT_TEMPLATE = """\
// {name}
// {url}
// Time: {time_limit} | Memory: {memory_limit} | Date: {date}
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    return 0;
}
"""

BINARY = "/tmp/cc_sol"
TIMEOUT = 5


def _settings():
    return sublime.load_settings("CompetitiveCompanionFOC.sublime-settings")


def _sol_path():
    return os.path.expanduser(_settings().get("sol_path", "~/cp/sol.cpp"))


def _port():
    return _settings().get("port", 10045)


def _render_template(data):
    tp = _settings().get("template_path", "")
    if tp:
        tp = os.path.expanduser(tp)
        if os.path.exists(tp):
            with open(tp) as f:
                src = f.read()
        else:
            src = DEFAULT_TEMPLATE
    else:
        src = DEFAULT_TEMPLATE

    limit_ms = data.get("timeLimit", "")
    limit_mb = data.get("memoryLimit", "")
    return (src
        .replace("{name}", data.get("name", ""))
        .replace("{url}", data.get("url", ""))
        .replace("{time_limit}", f"{limit_ms}ms" if limit_ms else "")
        .replace("{memory_limit}", f"{limit_mb}MB" if limit_mb else "")
        .replace("{date}", date.today().isoformat()))


# ── Verify ────────────────────────────────────────────────────────────────────

def _outputs_match(expected, actual):
    if _settings().get("match_mode", "token") == "none":
        return True
    return expected.split() == actual.split()


def _run_verify(sol, tests):
    window = sublime.active_window()
    panel = window.create_output_panel("cc_verify")
    panel.settings().set("word_wrap", False)
    window.run_command("show_panel", {"panel": "output.cc_verify"})

    def write(text):
        panel.run_command("append", {"characters": text, "scroll_to_end": True})

    proc = subprocess.Popen(
        ["g++", "-std=c++17", "-O2", sol, "-o", BINARY],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _, stderr = proc.communicate()
    if proc.returncode != 0:
        write("Compile error:\n" + stderr.decode("utf-8", errors="replace"))
        return

    passed = 0
    for i, t in enumerate(tests, 1):
        inp = t["input"]
        expected = t["output"].strip()
        try:
            proc = subprocess.Popen(
                [BINARY],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, _ = proc.communicate(
                input=inp.encode("utf-8"), timeout=TIMEOUT
            )
            actual = stdout.decode("utf-8", errors="replace").strip()
        except subprocess.TimeoutExpired:
            proc.kill()
            write("Test {}: TLE (>{}s)\n".format(i, TIMEOUT))
            continue

        if _outputs_match(expected, actual):
            write("Test {}: PASS\n".format(i))
            passed += 1
        else:
            write("Test {}: FAIL\n".format(i))
            inp_preview = inp.strip().replace("\n", " | ")
            exp_preview = expected.strip().replace("\n", " | ")
            got_preview = actual.strip().replace("\n", " | ") if actual.strip() else "(empty)"
            write("  in:  {}\n".format(inp_preview))
            write("  exp: {}\n".format(exp_preview))
            write("  got: {}\n".format(got_preview))

    write("\n{}/{} passed\n".format(passed, len(tests)))


# ── HTTP handler ──────────────────────────────────────────────────────────────

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
    tests = data.get("tests", [])
    name = data.get("name", "problem")

    if _settings().get("per_problem_dir", False):
        slug = "".join(c if c.isalnum() or c in " _-" else "" for c in name).strip().replace(" ", "_")
        base = os.path.dirname(os.path.expanduser(_sol_path()))
        problem_dir = os.path.join(base, slug)
        os.makedirs(problem_dir, exist_ok=True)
        sol = os.path.join(problem_dir, "sol.cpp")
    else:
        sol = _sol_path()

    with open(sol, "w") as f:
        f.write(_render_template(data))

    with open(sol + ":tests", "w") as f:
        json.dump([{"test": t["input"]} for t in tests], f, indent=2)

    with open(sol + ":expected", "w") as f:
        json.dump([{"output": t["output"]} for t in tests], f, indent=2)

    window = sublime.active_window()
    view = window.open_file(sol)
    sublime.status_message("CC: {} ({} tests)".format(name, len(tests)))

    auto_foc = _settings().get("auto_run_foc", True)
    auto_verify = _settings().get("auto_verify", True)

    def _after_load():
        if view.is_loading():
            sublime.set_timeout(_after_load, 100)
            return

        window.focus_view(view)

        if auto_foc:
            view.run_command("view_tester", {"action": "make_opd", "use_debugger": False})

        if auto_verify and tests:
            threading.Thread(
                target=_run_verify, args=(sol, tests), daemon=True
            ).start()

    sublime.set_timeout(_after_load, 200)


# ── Server lifecycle ──────────────────────────────────────────────────────────

def _start():
    global _server
    with _lock:
        if _server is not None:
            return False
        try:
            _server = HTTPServer(("", _port()), _Handler)
        except OSError as e:
            sublime.error_message(
                "CompetitiveCompanionFOC: could not bind port {}\n{}".format(_port(), e)
            )
            return False
        threading.Thread(target=_server.serve_forever, daemon=True).start()
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
        sublime.status_message(
            "Competitive Companion listening on port {}".format(_port())
        )


def plugin_unloaded():
    _stop()


# ── Commands ──────────────────────────────────────────────────────────────────

class CcStartListenerCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        if _start():
            sublime.status_message("CC listener started on port {}".format(_port()))
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
            sublime.status_message("CC listener restarted on port {}".format(_port()))


class CcStatusCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        status = "RUNNING" if _server is not None else "STOPPED"
        sublime.message_dialog(
            "Competitive Companion listener is {} on port {}".format(status, _port())
        )


class CcVerifyCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        sol = _sol_path()
        tests_path = sol + ":tests"
        expected_path = sol + ":expected"

        if not os.path.exists(tests_path) or not os.path.exists(expected_path):
            sublime.status_message("CC: no test data found for current problem")
            return

        with open(tests_path) as f:
            inputs = json.load(f)
        with open(expected_path) as f:
            outputs = json.load(f)

        tests = [{"input": inp["test"], "output": out["output"]}
                 for inp, out in zip(inputs, outputs)]

        threading.Thread(
            target=_run_verify, args=(sol, tests), daemon=True
        ).start()
