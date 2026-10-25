
"""
فحص بيانات المشتركين في OneSignal.
قراءة فقط: لا يرسل إشعارات ولا يعدل البيانات.
"""

import json
import os
import sys
import urllib.error
import urllib.request

APP_ID = "e41737a2-7d31-4a24-8a49-cbfc4e75aff0"
API_URL = "https://api.onesignal.com/apps/{}/users"


def check_subscribers():
    api_key = os.environ.get("ONESIGNAL_REST_API_KEY")

    if not api_key:
        print("ERROR: OneSignal API key is missing.")
        return 1

    url = API_URL.format(APP_ID) + "?limit=100"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": "Key " + api_key,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=30
        ) as response:
            data = json.load(response)

    except urllib.error.HTTPError as error:
        print("HTTP error:", error.code)
        return 1

    except Exception as error:
        print("Connection error:", type(error).__name__)
        return 1

    users = data.get("users", [])

    print("Users returned:", len(users))

    valid_locations = 0
    missing_locations = 0

    for user in users:
        properties = user.get("properties") or {}
        tags = properties.get("tags") or {}

        coords = tags.get("prayer_coords")
        timezone = tags.get("prayer_timezone")

        if not coords or not timezone:
            missing_locations += 1
            continue

        try:
            latitude, longitude = map(
                float, coords.split(",")
            )

            if not (
                -90 <= latitude <= 90
                and -180 <= longitude <= 180
            ):
                raise ValueError("Invalid coordinates")

        except (ValueError, AttributeError):
            missing_locations += 1
            continue

        valid_locations += 1

    print("Users with valid location:", valid_locations)
    print("Users missing valid location:", missing_locations)

    if data.get("next_cursor"):
        print(
            "NOTE: More users exist; "
            "this check covers only the first page."
        )

    print("Read-only check completed.")
    return 0


if __name__ == "__main__":
    sys.exit(check_subscribers())
