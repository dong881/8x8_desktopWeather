# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `.gitignore` file to exclude Python cache, virtual environments, and IDE files
- Logging module with configurable log levels (replaces print statements)
- Signal handling (SIGTERM/SIGINT) for graceful shutdown
- `if __name__ == '__main__'` guard for better testability
- Helper functions: `_format_hour`, `_build_api_url`, `_validate_api_response`, `_extract_weather_data`, `_extract_pop_value`, `_validate_config`, `_set_brightness`
- Configurable constants: `LOCATION_NAME`, `API_BASE_URL`, `API_DATASET_TEMP`, `API_DATASET_POP`, `TEMP_DISPLAY_MIN`, `TEMP_DISPLAY_MAX`, `NIGHT_MODE_START`, `NIGHT_MODE_END`, `BRIGHTNESS_NIGHT`, `BRIGHTNESS_DAY`, `MAX_CONTRAST`, `API_TIMEOUT`
- Environment variable support for API token (`CWA_AUTH_TOKEN`)
- Default fallback data constants (`DEFAULT_TEMPERATURE`, `DEFAULT_POP`, etc.)
- Module-level constants: `DIGIT_FONT`, `MODE_DURATIONS`, `MODE_NAMES`, `POP_FIELD_NAMES`
- Comprehensive unit tests (62 tests) covering core logic functions
- Display mode documentation in README
- Customization section in README with all configurable options
- CHANGELOG.md

### Fixed
- Typo `delat` variable (removed unused)
- `exit()` → `sys.exit(1)` with proper exit code
- `PoP_to_led_levels` redundant condition (p>=20 and p<20 both returned `[0,0]`)
- Contrast overflow protection (`min(intensity * 16, MAX_CONTRAST)`)
- Inconsistent default data array lengths
- `NowTime` manual zero-padding → `strftime('%H')`
- `shift_array` now handles empty arrays
- `show_data_update_animation` properly clears display
- `display_heights` array bounds checking
- README references to old filename `SmartWeather.py` → `Weather.py`
- README `libtiff5` → `libtiff-dev` in manual setup
- `install.sh` no longer modifies `requirements_system.txt` in-place
- `install.sh` uses absolute paths for `PROJECT_DIR` and `VENV_DIR`
- `install.sh` supports newer Pi OS SPI config path (`/boot/firmware/config.txt`)

### Changed
- Replaced `print()` statements with `logging` module
- Simplified `calculate_output` with math formula
- Simplified `calculate_output_forPoP` with math formula
- Extracted duplicated API validation code into `_validate_api_response`
- Extracted duplicated URL construction into `_build_api_url`
- Extracted brightness setting into `_set_brightness` helper
- `DIGIT_FONT` moved from function scope to module-level constant
- `config.py` supports environment variable `CWA_AUTH_TOKEN`
- `.env` cleaned up to only include relevant project configurations
- Main loop moved into `main()` function
- Animation frame counter resets on mode switch

### Removed
- Unused `import random`
- `__pycache__` directory from repository tracking
- Unrelated configurations from `.env` (Google API, Gemini, Redis, Notion, etc.)
