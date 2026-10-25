
"""
فحص بيانات مستخدم واحد في OneSignal.
قراءة فقط: لا يرسل إشعارات ولا يعدل البيانات.
"""

import json
import os
import sys
import urllib.error
import urllib.request

APP_ID = "e41737a2-7d31-4a24-8a49-cbfc4e75aff0"

USER_ID = (
    "c9796f0b-c6ae-4c13-9514-b11f629ff869"
)


def check_subscriber():
    api_key = os.environ.get("ONESIGNAL_REST_API_KEY")

    if not api_key:
        print("ERROR: OneSignal API key is missing.")
        return 1

    url = (
        f"https://api.onesignal.com/apps/{APP_ID}"
        f"/users/by/onesignal_id/{USER_ID}"
    )

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

    properties = data.get("properties") or {}
    tags = properties.get("tags") or {}

    coords = tags.get("prayer_coords")
    timezone = tags.get("prayer_timezone")

    print("User record found: YES")
    print("Prayer coordinates present:", bool(coords))
    print("Prayer timezone present:", bool(timezone))

    if not coords or not timezone:
        print("RESULT: Location data incomplete.")
        return 1

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
        print("RESULT: Invalid coordinates.")
        return 1

    print("RESULT: Location data valid.")
    print("Read-only check completed.")
    return 0


if __name__ == "__main__":
    sys.exit(check_subscriber())
