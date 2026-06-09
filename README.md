# CompetitiveCompanionFOC

A Sublime Text 4 package that bridges the [Competitive Companion](https://github.com/jmerle/competitive-companion) browser extension with [FastOlympicCoding](https://packagecontrol.io/packages/FastOlympicCoding).

When you click the Competitive Companion button on any problem page, this package:

1. Rewrites your solution file with a clean template (including problem name, URL, and limits)
2. Loads all sample test cases into FOC's format
3. Compiles and runs them automatically, no keypress needed

## Compared to FastOlympicCodingHook

[FastOlympicCodingHook](https://github.com/DrSwad/FastOlympicCodingHook) requires you to right-click and start a listener per file, then manually run tests after. This package starts automatically with Sublime and triggers FOC without any extra steps.

## Requirements

- **Sublime Text 4** (build 4050+) — ST3 is not supported
- [FastOlympicCoding](https://packagecontrol.io/packages/FastOlympicCoding) installed
- [Competitive Companion](https://github.com/jmerle/competitive-companion) browser extension configured to send to port `10045`

## Installation

### Via Package Control (recommended)

Search for `CompetitiveCompanionFOC` in Package Control.

### Manual

Clone this repo into your Sublime Text `Packages` directory:

```
git clone https://github.com/ravenZ3/CompetitiveCompanionFOC \
  ~/.config/sublime-text/Packages/CompetitiveCompanionFOC
```

## Configuration

Open `Preferences > Package Settings > CompetitiveCompanionFOC > Settings` to configure. Your overrides go in the right pane.

| Key | Default | Description |
|---|---|---|
| `port` | `10045` | Port Competitive Companion sends to |
| `sol_path` | `~/cp/sol.cpp` | Solution file overwritten each problem (or base dir for `per_problem_dir`) |
| `template_path` | `""` | Path to a `.cpp` template file. Falls back to built-in if empty |
| `auto_run_foc` | `true` | Auto-load test cases into FOC when a problem arrives |
| `auto_verify` | `true` | Auto-compile and diff against expected outputs when a problem arrives |
| `per_problem_dir` | `false` | Create a separate directory per problem (e.g. `~/cp/Watermelon/sol.cpp`) |
| `match_mode` | `"token"` | `"token"` — compare whitespace-split tokens (matches how judges work); `"none"` — disable verification |

## Template Placeholders

If you use a custom `template_path`, you can use these placeholders:

| Placeholder | Example |
|---|---|
| `{name}` | `Watermelon` |
| `{url}` | `https://codeforces.com/contest/4/problem/A` |
| `{time_limit}` | `2000ms` |
| `{memory_limit}` | `64MB` |
| `{date}` | `2026-06-09` |

## Commands

Available from `Tools > Competitive Companion` and the command palette (`Ctrl+Shift+P`):

| Command | Description |
|---|---|
| `CC: Start Listener` | Start the HTTP listener |
| `CC: Stop Listener` | Stop the HTTP listener |
| `CC: Restart Listener` | Restart the HTTP listener |
| `CC: Listener Status` | Show whether the listener is running |
| `CC: Verify Tests` | Manually re-run test verification |

## License

MIT
