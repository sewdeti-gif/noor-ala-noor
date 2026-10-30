
"""جدولة تنبيهات شوايل الآخرة حسب الموقع والتوقيت المحلي.

15 تنبيهًا في الأيام العادية، و19 تنبيهًا يوم الجمعة.
المواقيت حسابية وتحتاج المقارنة بالتقويم المحلي قبل الاعتماد.
"""

import argparse
import json
import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from astral import LocationInfo
from astral.sun import (
    SunDirection,
    elevation,
    sun,
    time_at_elevation,
)

SLOGAN = "دقائق مع القرآن، سكينة للقلب وزاد للآخرة."


def schedule_for_day(day, lat, lon, timezone):
    if not -90 <= lat <= 90:
        raise ValueError("خط العرض غير صحيح")
    if not -180 <= lon <= 180:
        raise ValueError("خط الطول غير صحيح")

    tz = ZoneInfo(timezone)

    observer = LocationInfo(
        "User", "", timezone, lat, lon
    ).observer

    solar = sun(observer, date=day, tzinfo=tz)

    fajr = time_at_elevation(
        observer,
        -18,
        day,
        SunDirection.RISING,
        tzinfo=tz,
    )

    isha = time_at_elevation(
        observer,
        -18,
        day,
        SunDirection.SETTING,
        tzinfo=tz,
    )

    dhuhr = solar["noon"]
    maghrib = solar["sunset"]

    noon_altitude = elevation(observer, dhuhr)

    noon_shadow = 1 / math.tan(
        math.radians(noon_altitude)
    )

    asr_altitude = math.degrees(
        math.atan(1 / (1 + noon_shadow))
    )

    asr = time_at_elevation(
        observer,
        asr_altitude,
        day,
        SunDirection.SETTING,
        tzinfo=tz,
    )

    previous_maghrib = sun(
        observer,
        date=day - timedelta(days=1),
        tzinfo=tz,
    )["sunset"]

    last_third = (
        previous_maghrib
        + (fajr - previous_maghrib) * 2 / 3
    )

    events = [
        (
            "fajr_1",
            fajr + timedelta(minutes=30),
            "بعد الفجر — سورة يس",
        ),
        (
            "fajr_2",
            fajr + timedelta(minutes=60),
            "تذكير بسورة يس",
        ),
        (
            "dhuhr_1",
            dhuhr + timedelta(minutes=60),
            "بعد الظهر — سورة الفتح",
        ),
        (
            "dhuhr_2",
            dhuhr + timedelta(minutes=120),
            "تذكير بسورة الفتح",
        ),
        (
            "asr_1",
            asr + timedelta(minutes=30),
            "بعد العصر — سورة النبأ",
        ),
        (
            "asr_2",
            asr + timedelta(minutes=120),
            "تذكير بسورة النبأ",
        ),
        (
            "maghrib_1",
            maghrib + timedelta(minutes=10),
            "بعد المغرب — سورة الواقعة",
        ),
        (
            "maghrib_2",
            maghrib + timedelta(minutes=40),
            "تذكير بسورة الواقعة",
        ),
        (
            "isha_1",
            isha + timedelta(minutes=10),
            "بعد العشاء — سورة الملك",
        ),
        (
            "isha_2",
            isha + timedelta(minutes=40),
            "تذكير بسورة الملك",
        ),
        (
            "qiyam_last_third",
            last_third,
            "دخل الثلث الأخير من الليل، وقت الدعاء والاستغفار والقيام",
        ),
        (
            "qiyam_1",
            fajr - timedelta(minutes=60),
            "قيام الليل — والذين يبيتون لربهم سجدًا وقيامًا",
        ),
        (
            "qiyam_2",
            fajr - timedelta(minutes=30),
            "قيام الليل — تتجافى جنوبهم عن المضاجع",
        ),
        (
            "duha_1",
            datetime(
                day.year,
                day.month,
                day.day,
                9,
                tzinfo=tz,
            ),
            "حان وقت صلاة الضحى",
        ),
        (
            "duha_2",
            dhuhr - timedelta(minutes=30),
            "تذكير بصلاة الضحى",
        ),
    ]

    if day.weekday() == 4:
        events.extend([
            (
                "friday_kahf_1",
                fajr + timedelta(minutes=65),
                "الجمعة — تذكير بسورة الكهف",
            ),
            (
                "friday_kahf_2",
                dhuhr + timedelta(minutes=65),
                "الجمعة — لا تنس سورة الكهف",
            ),
            (
                "friday_dua_1",
                asr + timedelta(minutes=30),
                "الجمعة — الإكثار من الدعاء",
            ),
            (
                "friday_dua_2",
                maghrib - timedelta(minutes=60),
                "الجمعة — اغتنم الساعة الأخيرة بالدعاء",
            ),
        ])

    events.sort(key=lambda item: item[1])

    result = [
        {
            "id": event_id,
            "time": event_time.isoformat(),
            "message": message + ". " + SLOGAN,
        }
        for event_id, event_time, message in events
    ]

    expected = 19 if day.weekday() == 4 else 15

    if len(result) != expected:
        raise RuntimeError(
            f"Expected {expected} notifications, "
            f"got {len(result)}"
        )

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--lat", type=float, required=True
    )
    parser.add_argument(
        "--lon", type=float, required=True
    )
    parser.add_argument(
        "--tz", required=True
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
    )

    args = parser.parse_args()

    reminders = schedule_for_day(
        date.fromisoformat(args.date),
        args.lat,
        args.lon,
        args.tz,
    )

    print(
        json.dumps(
            reminders,
            ensure_ascii=False,
            indent=2,
        )
    )
