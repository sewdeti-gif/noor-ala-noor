
"""جدولة تنبيهات تطبيق شوايل الآخرة.
14 تنبيهًا في الأيام العادية، و18 يوم الجمعة.
حساب المواقيت أولي ويحتاج التحقق قبل التشغيل العام.
"""

import argparse
import json
import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from astral import LocationInfo
from astral.sun import SunDirection, elevation, sun, time_at_elevation

SLOGAN = "دقائق مع القرآن، سكينة للقلب وزاد للآخرة."


def schedule_for_day(day, lat, lon, timezone):
    tz = ZoneInfo(timezone)
    loc = LocationInfo("User", "", timezone, lat, lon)
    observer = loc.observer
    solar = sun(observer, date=day, tzinfo=tz)

    fajr = time_at_elevation(
        observer, -18, day, SunDirection.RISING, tzinfo=tz
    )
    isha = time_at_elevation(
        observer, -18, day, SunDirection.SETTING, tzinfo=tz
    )

    dhuhr = solar["noon"]
    sunset = solar["sunset"]

    noon_altitude = elevation(observer, dhuhr)
    noon_shadow = 1 / math.tan(math.radians(noon_altitude))
    asr_altitude = math.degrees(
        math.atan(1 / (1 + noon_shadow))
    )
    asr = time_at_elevation(
        observer, asr_altitude, day,
        SunDirection.SETTING, tzinfo=tz
    )

    events = [
        ("fajr_1", fajr + timedelta(minutes=30),
         "صلاة الفجر — سورة يس"),

        ("fajr_2", fajr + timedelta(minutes=60),
         "ورد الفجر — سورة يس"),

        ("dhuhr_1", dhuhr + timedelta(minutes=60),
         "صلاة الظهر — سورة الفتح"),

        ("dhuhr_2", dhuhr + timedelta(minutes=120),
         "ورد الظهر — سورة الفتح"),

        ("asr_1", asr + timedelta(minutes=30),
         "صلاة العصر — سورة النبأ"),

        ("asr_2", asr + timedelta(minutes=120),
         "ورد العصر — سورة النبأ"),

        ("maghrib_1", sunset + timedelta(minutes=10),
         "صلاة المغرب — سورة الواقعة"),

        ("maghrib_2", sunset + timedelta(minutes=40),
         "ورد المغرب — سورة الواقعة"),

        ("isha_1", isha + timedelta(minutes=10),
         "صلاة العشاء — سورة الملك"),

        ("isha_2", isha + timedelta(minutes=40),
         "ورد العشاء — سورة الملك"),

        ("qiyam_1", fajr - timedelta(minutes=30),
         "قيام الليل — ﴿وَالَّذِينَ يَبِيتُونَ لِرَبِّهِمْ سُجَّدًا وَقِيَامًا﴾ [الفرقان: 64]"),

        ("qiyam_2", fajr - timedelta(minutes=15),
         "قيام الليل — ﴿تَتَجَافَىٰ جُنُوبُهُمْ عَنِ الْمَضَاجِعِ﴾ [السجدة: 16]"),

        ("duha_1", datetime(
            day.year, day.month, day.day,
            9, tzinfo=tz
        ), "صلاة الضحى"),

        ("duha_2", dhuhr - timedelta(minutes=30),
         "تذكير بصلاة الضحى"),
    ]

    if day.weekday() == 4:
        events.extend([
            ("friday_kahf_1",
             fajr + timedelta(minutes=65),
             "الجمعة — سورة الكهف"),

            ("friday_kahf_2",
             dhuhr + timedelta(minutes=65),
             "الجمعة — سورة الكهف"),

            ("friday_dua_1",
             asr + timedelta(minutes=30),
             "الجمعة — الإكثار من الدعاء"),

            ("friday_dua_2",
             sunset - timedelta(minutes=60),
             "الجمعة — الدعاء قبل المغرب"),
        ])

    return [
        {
            "id": key,
            "time": when.isoformat(),
            "message": message + ". " + SLOGAN,
        }
        for key, when, message in sorted(
            events, key=lambda item: item[1]
        )
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lat", type=float, required=True
    )
    parser.add_argument(
        "--lon", type=float, required=True
    )
    parser.add_argument("--tz", required=True)
    parser.add_argument(
        "--date", default=date.today().isoformat()
    )
    args = parser.parse_args()

    result = schedule_for_day(
        date.fromisoformat(args.date),
        args.lat,
        args.lon,
        args.tz
    )

    print(json.dumps(
        result, ensure_ascii=False, indent=2
    ))
