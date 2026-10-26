
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from prayer_scheduler import schedule_for_day

# اختبار المواقيت في بلدان مختلفة
LOCATIONS = [
    ("نواكشوط", 18.0735, -15.9582, "Africa/Nouakchott"),
    ("الدوحة", 25.2854, 51.5310, "Asia/Qatar"),
    ("الرياض", 24.7136, 46.6753, "Asia/Riyadh"),
    ("باريس", 48.8566, 2.3522, "Europe/Paris"),
]

def check_location(name, latitude, longitude, timezone):
    today = datetime.now(ZoneInfo(timezone)).date()

    events = schedule_for_day(
        today,
        latitude,
        longitude,
        timezone
    )

    expected = 19 if today.weekday() == 4 else 15
    assert len(events) == expected

    required = [
        "qiyam_last_third",
        "qiyam_1",
        "qiyam_2",
    ]

    print("\nالمدينة:", name)
    print("التاريخ:", today)

    for event_id in required:
        event = next(
            (e for e in events if e["id"] == event_id),
            None
        )

        assert event is not None, (
            "تنبيه مفقود: " + event_id
        )

        when = datetime.fromisoformat(event["time"])

        assert when.tzinfo is not None
        assert when.utcoffset() is not None

        print(event_id, ":", when.strftime("%H:%M"))

    print("نجح اختبار حساب المواقيت")

for location in LOCATIONS:
    check_location(*location)

print("\nاكتملت جميع اختبارات المواقيت بنجاح")
