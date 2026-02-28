# ============================================================
# Weather API Configuration
# ============================================================
# Get your CWA authorization token from:
# https://opendata.cwa.gov.tw/user/authkey
#
# You can set the token in two ways:
# 1. Edit this file directly (replace the placeholder below)
# 2. Set the CWA_AUTH_TOKEN environment variable
# ============================================================
import os

_env_token = os.environ.get('CWA_AUTH_TOKEN', '').strip()

WeatherAPI = {
    'Authorization': _env_token if _env_token else 'CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
    # Replace with your actual token, e.g.:
    # 'Authorization': 'CWA-12345678-ABCD-EFGH-IJKL-1234567890AB'
}
