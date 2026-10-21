"""Refresh flights.json from Taoyuan Airport's public flight file.

The airport file only covers yesterday / today / tomorrow, so each run merges
into the existing flights.json and builds up a weekly pattern per flight.
Run daily: python3 update_flights.py
"""
import json, os, sys, urllib.request
from datetime import date, datetime, timedelta

SRC = "https://www.taoyuan-airport.com/uploads/flightx/a_flight_v4.txt"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flights.json")
KEEP_DAYS = 21  # drop weekday entries not seen for this long


def fetch(path=None):
    if path:
        raw = open(path, "rb").read()
    else:
        req = urllib.request.Request(SRC, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=60).read()
    return raw.decode("big5hkscs", errors="replace")


def parse(text):
    rows = []
    for line in text.splitlines():
        c = [x.strip() for x in line.split(",")]
        if len(c) < 13 or c[1] not in ("A", "D"):
            continue
        num = c[4].lstrip("0") or "0"
        rows.append({
            "term": c[0], "dir": c[1], "code": c[2] + num, "airline": c[3],
            "date": c[6].replace("/", "-"), "time": c[7][:5],
            "city": c[12] or c[11], "status": c[13],
        })
    return rows


def main():
    rows = parse(fetch(sys.argv[1] if len(sys.argv) > 1 else None))
    if not rows:
        sys.exit("No flights parsed; keeping existing flights.json")
    try:
        data = json.load(open(OUT, encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        data = {"flights": {}, "airlines": {}}

    today = date.today()
    flights, airlines = data["flights"], data["airlines"]
    dates = {}  # exact schedule for the dates in this file
    for r in rows:
        if "取消" in r["status"] or "CANCEL" in r["status"].upper():
            continue
        wd = str(datetime.strptime(r["date"], "%Y-%m-%d").isoweekday())  # 1=Mon
        entry = [r["time"], int(r["term"]), r["city"], r["date"]]
        flights.setdefault(r["code"], {}).setdefault(r["dir"], {})[wd] = entry
        dates.setdefault(r["date"], {})[r["code"] + r["dir"]] = entry[:3]
        airlines.setdefault(r["code"].rstrip("0123456789"), {})[r["term"]] = r["airline"]

    cutoff = (today - timedelta(days=KEEP_DAYS)).isoformat()
    for code in list(flights):
        for d in list(flights[code]):
            flights[code][d] = {w: e for w, e in flights[code][d].items() if e[3] >= cutoff}
            if not flights[code][d]:
                del flights[code][d]
        if not flights[code]:
            del flights[code]

    data.update(updated=datetime.now().strftime("%Y-%m-%d %H:%M"), dates=dates)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(flights)} flights, dates {sorted(dates)}, written {OUT}")


if __name__ == "__main__":
    main()
