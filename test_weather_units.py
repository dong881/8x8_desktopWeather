#!/usr/bin/env python3
"""Unit tests for Weather.py core functions.

Tests the pure logic functions that don't require hardware (LED matrix).
"""

import unittest
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestTemperatureToLedLevels(unittest.TestCase):
    """Tests for temperature_to_led_levels function."""

    def setUp(self):
        """Import the function under test."""
        # We need to mock the hardware imports before importing Weather
        self._mock_hardware()
        from Weather import temperature_to_led_levels
        self.func = temperature_to_led_levels

    def _mock_hardware(self):
        """Mock hardware-dependent modules."""
        import unittest.mock as mock
        # Mock luma modules to avoid SPI hardware dependency
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_basic_conversion(self):
        """Test basic temperature to level conversion."""
        result = self.func(['22', '25', '30'])
        self.assertEqual(len(result), 3)
        for level in result:
            self.assertGreaterEqual(level, 0)
            self.assertLessEqual(level, 7)

    def test_minimum_temperature(self):
        """Test temperature at minimum bound."""
        result = self.func(['12'])
        self.assertEqual(result, [0])

    def test_maximum_temperature(self):
        """Test temperature at maximum bound."""
        result = self.func(['33'])
        self.assertEqual(result, [7])

    def test_below_minimum_clamps(self):
        """Test temperature below minimum is clamped."""
        result = self.func(['5'])
        self.assertEqual(result, [0])

    def test_above_maximum_clamps(self):
        """Test temperature above maximum is clamped."""
        result = self.func(['40'])
        self.assertEqual(result, [7])

    def test_midpoint_temperature(self):
        """Test temperature at midpoint."""
        # Midpoint of 12-33 range is 22.5
        result = self.func(['23'])
        self.assertIn(result[0], [3, 4])  # Should be around middle

    def test_empty_list(self):
        """Test empty input list."""
        result = self.func([])
        self.assertEqual(result, [])

    def test_integer_input(self):
        """Test with integer input values."""
        result = self.func([22, 25, 30])
        self.assertEqual(len(result), 3)

    def test_eight_values(self):
        """Test with standard 8-value input."""
        temps = ['15', '18', '21', '24', '27', '30', '33', '12']
        result = self.func(temps)
        self.assertEqual(len(result), 8)
        # Should be monotonically increasing for first 7
        for i in range(6):
            self.assertLessEqual(result[i], result[i + 1])


class TestPoPToLedLevels(unittest.TestCase):
    """Tests for PoP_to_led_levels function."""

    def setUp(self):
        self._mock_hardware()
        from Weather import PoP_to_led_levels
        self.func = PoP_to_led_levels

    def _mock_hardware(self):
        import unittest.mock as mock
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_high_probability(self):
        """Test >=80% returns [1, 1]."""
        result = self.func(['80'])
        self.assertEqual(result, [1, 1])

    def test_medium_high_probability(self):
        """Test 60-79% returns [1, 0]."""
        result = self.func(['60'])
        self.assertEqual(result, [1, 0])

    def test_medium_probability(self):
        """Test 40-59% returns [0, 1]."""
        result = self.func(['40'])
        self.assertEqual(result, [0, 1])

    def test_low_probability(self):
        """Test <40% returns [0, 0]."""
        result = self.func(['20'])
        self.assertEqual(result, [0, 0])

    def test_zero_probability(self):
        """Test 0% returns [0, 0]."""
        result = self.func(['0'])
        self.assertEqual(result, [0, 0])

    def test_100_probability(self):
        """Test 100% returns [1, 1]."""
        result = self.func(['100'])
        self.assertEqual(result, [1, 1])

    def test_four_values(self):
        """Test standard 4-value input produces 8 levels."""
        result = self.func(['20', '50', '70', '90'])
        self.assertEqual(len(result), 8)

    def test_empty_list(self):
        """Test empty input."""
        result = self.func([])
        self.assertEqual(result, [])

    def test_invalid_input_returns_default(self):
        """Test invalid input returns default values."""
        result = self.func(['abc'])
        self.assertEqual(len(result), 8)
        self.assertTrue(all(v == 0 for v in result))


class TestCalculateOutput(unittest.TestCase):
    """Tests for calculate_output function."""

    def setUp(self):
        self._mock_hardware()
        from Weather import calculate_output
        self.func = calculate_output

    def _mock_hardware(self):
        import unittest.mock as mock
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_hour_0(self):
        """Test midnight maps to column 7."""
        self.assertEqual(self.func(0), 7)

    def test_hour_1_to_3(self):
        """Test hours 1-3 map to column 0."""
        for h in [1, 2, 3]:
            self.assertEqual(self.func(h), 0, f"Hour {h} should map to 0")

    def test_hour_4_to_6(self):
        """Test hours 4-6 map to column 1."""
        for h in [4, 5, 6]:
            self.assertEqual(self.func(h), 1, f"Hour {h} should map to 1")

    def test_hour_7_to_9(self):
        """Test hours 7-9 map to column 2."""
        for h in [7, 8, 9]:
            self.assertEqual(self.func(h), 2, f"Hour {h} should map to 2")

    def test_hour_10_to_12(self):
        """Test hours 10-12 map to column 3."""
        for h in [10, 11, 12]:
            self.assertEqual(self.func(h), 3, f"Hour {h} should map to 3")

    def test_hour_13_to_15(self):
        """Test hours 13-15 map to column 4."""
        for h in [13, 14, 15]:
            self.assertEqual(self.func(h), 4, f"Hour {h} should map to 4")

    def test_hour_16_to_18(self):
        """Test hours 16-18 map to column 5."""
        for h in [16, 17, 18]:
            self.assertEqual(self.func(h), 5, f"Hour {h} should map to 5")

    def test_hour_19_to_21(self):
        """Test hours 19-21 map to column 6."""
        for h in [19, 20, 21]:
            self.assertEqual(self.func(h), 6, f"Hour {h} should map to 6")

    def test_hour_22_to_23(self):
        """Test hours 22-23 map to column 7."""
        for h in [22, 23]:
            self.assertEqual(self.func(h), 7, f"Hour {h} should map to 7")

    def test_all_hours_valid(self):
        """Test all valid hours produce valid column indices."""
        for h in range(24):
            result = self.func(h)
            self.assertGreaterEqual(result, 0, f"Hour {h} produced negative index")
            self.assertLessEqual(result, 7, f"Hour {h} produced index > 7")


class TestCalculateOutputForPoP(unittest.TestCase):
    """Tests for calculate_output_forPoP function."""

    def setUp(self):
        self._mock_hardware()
        from Weather import calculate_output_forPoP
        self.func = calculate_output_forPoP

    def _mock_hardware(self):
        import unittest.mock as mock
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_hour_0(self):
        """Test midnight maps to column 7."""
        self.assertEqual(self.func(0), 7)

    def test_hours_1_to_6(self):
        """Test hours 1-6 map to column 1."""
        for h in range(1, 7):
            self.assertEqual(self.func(h), 1, f"Hour {h} should map to 1")

    def test_hours_7_to_12(self):
        """Test hours 7-12 map to column 3."""
        for h in range(7, 13):
            self.assertEqual(self.func(h), 3, f"Hour {h} should map to 3")

    def test_hours_13_to_18(self):
        """Test hours 13-18 map to column 5."""
        for h in range(13, 19):
            self.assertEqual(self.func(h), 5, f"Hour {h} should map to 5")

    def test_hours_19_to_23(self):
        """Test hours 19-23 map to column 7."""
        for h in range(19, 24):
            self.assertEqual(self.func(h), 7, f"Hour {h} should map to 7")


class TestShiftArray(unittest.TestCase):
    """Tests for shift_array function."""

    def setUp(self):
        self._mock_hardware()
        from Weather import shift_array
        self.func = shift_array

    def _mock_hardware(self):
        import unittest.mock as mock
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_empty_array(self):
        """Test empty input returns empty list."""
        result = self.func([], 0)
        self.assertEqual(result, [])

    def test_no_shift(self):
        """Test shift by 0 returns same data."""
        data = [1, 2, 3, 4, 5, 6, 7, 8]
        result = self.func(data, 0)
        self.assertEqual(len(result), len(data))

    def test_shift_preserves_length(self):
        """Test shift preserves array length."""
        data = [1, 2, 3, 4, 5, 6, 7, 8]
        for i in range(8):
            result = self.func(data, i)
            self.assertEqual(len(result), len(data))


class TestGetBrightnessForTime(unittest.TestCase):
    """Tests for get_brightness_for_time function."""

    def setUp(self):
        self._mock_hardware()
        from Weather import get_brightness_for_time, BRIGHTNESS_NIGHT, BRIGHTNESS_DAY
        self.func = get_brightness_for_time
        self.night = BRIGHTNESS_NIGHT
        self.day = BRIGHTNESS_DAY

    def _mock_hardware(self):
        import unittest.mock as mock
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_night_mode_midnight(self):
        """Test midnight returns night brightness."""
        self.assertEqual(self.func(0), self.night)

    def test_night_mode_3am(self):
        """Test 3 AM returns night brightness."""
        self.assertEqual(self.func(3), self.night)

    def test_night_mode_5am(self):
        """Test 5 AM returns night brightness."""
        self.assertEqual(self.func(5), self.night)

    def test_day_mode_6am(self):
        """Test 6 AM returns day brightness."""
        self.assertEqual(self.func(6), self.day)

    def test_day_mode_noon(self):
        """Test noon returns day brightness."""
        self.assertEqual(self.func(12), self.day)

    def test_day_mode_11pm(self):
        """Test 11 PM returns day brightness."""
        self.assertEqual(self.func(23), self.day)


class TestHelperFunctions(unittest.TestCase):
    """Tests for helper utility functions."""

    def setUp(self):
        self._mock_hardware()

    def _mock_hardware(self):
        import unittest.mock as mock
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_format_hour(self):
        """Test _format_hour returns zero-padded hour string."""
        from Weather import _format_hour
        from datetime import datetime
        dt = datetime(2024, 1, 1, 8, 0, 0)
        self.assertEqual(_format_hour(dt), '08')

    def test_format_hour_midnight(self):
        """Test _format_hour for midnight."""
        from Weather import _format_hour
        from datetime import datetime
        dt = datetime(2024, 1, 1, 0, 0, 0)
        self.assertEqual(_format_hour(dt), '00')

    def test_format_hour_afternoon(self):
        """Test _format_hour for afternoon."""
        from Weather import _format_hour
        from datetime import datetime
        dt = datetime(2024, 1, 1, 15, 0, 0)
        self.assertEqual(_format_hour(dt), '15')

    def test_build_api_url(self):
        """Test _build_api_url constructs valid URL."""
        from Weather import _build_api_url
        url = _build_api_url('F-D0047-061', 'TOKEN', 'T', '2024-01-01', '08', '2024-01-02', '08')
        self.assertIn('F-D0047-061', url)
        self.assertIn('TOKEN', url)
        self.assertIn('2024-01-01', url)

    def test_validate_api_response_valid(self):
        """Test _validate_api_response with valid data."""
        from Weather import _validate_api_response
        valid_data = {
            "success": "true",
            "records": {
                "Locations": [{
                    "Location": [{"WeatherElement": []}]
                }]
            }
        }
        self.assertTrue(_validate_api_response(valid_data))

    def test_validate_api_response_invalid(self):
        """Test _validate_api_response with invalid data."""
        from Weather import _validate_api_response
        self.assertFalse(_validate_api_response({}))
        self.assertFalse(_validate_api_response({"success": "false"}))
        self.assertFalse(_validate_api_response({"success": "true", "records": {}}))

    def test_extract_pop_value_pop6h(self):
        """Test _extract_pop_value with PoP6h field."""
        from Weather import _extract_pop_value
        self.assertEqual(_extract_pop_value({'PoP6h': '30'}), '30')

    def test_extract_pop_value_pop(self):
        """Test _extract_pop_value with PoP field."""
        from Weather import _extract_pop_value
        self.assertEqual(_extract_pop_value({'PoP': '50'}), '50')

    def test_extract_pop_value_probability(self):
        """Test _extract_pop_value with ProbabilityOfPrecipitation field."""
        from Weather import _extract_pop_value
        self.assertEqual(
            _extract_pop_value({'ProbabilityOfPrecipitation': '40'}), '40'
        )

    def test_extract_pop_value_none(self):
        """Test _extract_pop_value with no precipitation field."""
        from Weather import _extract_pop_value
        self.assertIsNone(_extract_pop_value({'Temperature': '25'}))

    def test_extract_pop_value_empty(self):
        """Test _extract_pop_value with empty dict."""
        from Weather import _extract_pop_value
        self.assertIsNone(_extract_pop_value({}))


class TestConstants(unittest.TestCase):
    """Tests for configuration constants."""

    def setUp(self):
        self._mock_hardware()

    def _mock_hardware(self):
        import unittest.mock as mock
        luma_mock = mock.MagicMock()
        sys.modules['luma'] = luma_mock
        sys.modules['luma.led_matrix'] = luma_mock
        sys.modules['luma.led_matrix.device'] = luma_mock
        sys.modules['luma.core'] = luma_mock
        sys.modules['luma.core.interface'] = luma_mock
        sys.modules['luma.core.interface.serial'] = luma_mock
        sys.modules['luma.core.render'] = luma_mock

    def test_temp_range_valid(self):
        """Test temperature range is valid."""
        from Weather import TEMP_DISPLAY_MIN, TEMP_DISPLAY_MAX
        self.assertLess(TEMP_DISPLAY_MIN, TEMP_DISPLAY_MAX)

    def test_brightness_range(self):
        """Test brightness values are in valid range."""
        from Weather import BRIGHTNESS_NIGHT, BRIGHTNESS_DAY, MAX_CONTRAST
        self.assertGreaterEqual(BRIGHTNESS_NIGHT, 0)
        self.assertLessEqual(BRIGHTNESS_NIGHT, MAX_CONTRAST)
        self.assertGreaterEqual(BRIGHTNESS_DAY, 0)
        self.assertLessEqual(BRIGHTNESS_DAY, MAX_CONTRAST)

    def test_mode_constants(self):
        """Test display mode constants are distinct."""
        from Weather import MODE_BARGRAPH, MODE_TICKER, MODE_ICON, MODE_DEMO
        modes = [MODE_BARGRAPH, MODE_TICKER, MODE_ICON, MODE_DEMO]
        self.assertEqual(len(set(modes)), 4)

    def test_default_data_lengths(self):
        """Test default data arrays have correct lengths."""
        from Weather import DEFAULT_T_RAW, DEFAULT_POP_RAW, DEFAULT_T_LEVELS, DEFAULT_POP_LEVELS
        self.assertEqual(len(DEFAULT_T_RAW), 8)
        self.assertEqual(len(DEFAULT_POP_RAW), 4)
        self.assertEqual(len(DEFAULT_T_LEVELS), 8)
        self.assertEqual(len(DEFAULT_POP_LEVELS), 8)

    def test_digit_font_completeness(self):
        """Test DIGIT_FONT has all needed characters."""
        from Weather import DIGIT_FONT
        required_chars = set('0123456789 °%-:')
        self.assertTrue(required_chars.issubset(set(DIGIT_FONT.keys())))

    def test_digit_font_dimensions(self):
        """Test each DIGIT_FONT character is 3x5."""
        from Weather import DIGIT_FONT
        for char, pattern in DIGIT_FONT.items():
            self.assertEqual(len(pattern), 5, f"Char '{char}' should have 5 rows")
            for row in pattern:
                self.assertEqual(len(row), 3, f"Char '{char}' rows should have 3 columns")

    def test_pop_field_names(self):
        """Test POP_FIELD_NAMES contains expected field names."""
        from Weather import POP_FIELD_NAMES
        self.assertIn('PoP6h', POP_FIELD_NAMES)
        self.assertIn('PoP', POP_FIELD_NAMES)
        self.assertIn('ProbabilityOfPrecipitation', POP_FIELD_NAMES)

    def test_mode_durations(self):
        """Test MODE_DURATIONS has entries for all modes."""
        from Weather import MODE_DURATIONS, MODE_BARGRAPH, MODE_TICKER, MODE_ICON, MODE_DEMO
        self.assertIn(MODE_BARGRAPH, MODE_DURATIONS)
        self.assertIn(MODE_TICKER, MODE_DURATIONS)
        self.assertIn(MODE_ICON, MODE_DURATIONS)
        self.assertIn(MODE_DEMO, MODE_DURATIONS)

    def test_mode_names(self):
        """Test MODE_NAMES has entries for all modes."""
        from Weather import MODE_NAMES, NUM_MODES
        self.assertGreaterEqual(len(MODE_NAMES), NUM_MODES)


if __name__ == '__main__':
    unittest.main()
