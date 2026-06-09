# CompetitiveCompanionFOC

A Sublime Text package that bridges the [Competitive Companion](https://github.com/jmerle/competitive-companion) browser extension with [FastOlympicCoding](https://packagecontrol.io/packages/FastOlympicCoding).

When you click the Competitive Companion button on any problem page, this package:

1. Rewrites your solution file with a clean template
2. Loads all sample test cases into FOC's format
3. Compiles and runs them automatically, no keypress needed

## Compared to FastOlympicCodingHook

[FastOlympicCodingHook](https://github.com/DrSwad/FastOlympicCodingHook) requires you to right-click and start a listener per file, then manually run tests after. This package starts automatically with Sublime and triggers FOC without any extra steps.

## Requirements

- Sublime Text 4
- [FastOlympicCoding](https://packagecontrol.io/packages/FastOlympicCoding) installed
- [Competitive Companion](https://github.com/jmerle/competitive-companion) browser extension set to port `10045`

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

Go to `Preferences > Package Settings > CompetitiveCompanionFOC > Settings` or create:

`Packages/User/CompetitiveCompanionFOC.sublime-settings`

```json
{
    "port": 10045,
    "sol_path": "~/cp/sol.cpp",
    "template_path": "~/cp/template.cpp",
    "auto_run_foc": true
}
```

| Key | Default | Description |
|---|---|---|
| `port` | `10045` | Port Competitive Companion sends to |
| `sol_path` | `~/cp/sol.cpp` | File that gets overwritten each problem |
| `template_path` | `""` | Path to a `.cpp` template file. Falls back to a built-in template if empty |
| `auto_run_foc` | `true` | Auto-compile and run tests when a problem arrives |

## Commands

Available from the command palette (`Ctrl+Shift+P`) and `Tools > Competitive Companion`:

- `CC: Start Listener`
- `CC: Stop Listener`
- `CC: Restart Listener`
- `CC: Listener Status`

## License

MIT
