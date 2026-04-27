"""
disaster_alerts.py
──────────────────
Queries the GDACS (Global Disaster Alert and Coordination System) REST API
to pull live, real-time disaster alerts.  This gives the simulation
real-world context — victim severity and scenario framing are calibrated
from actual ongoing (or recent) disaster events.

Data source : GDACS (UN / EC Joint Research Centre)
API docs    : https://www.gdacs.org/gdacsapi/swagger/index.html
Auth        : None required
License     : Open, cite as "Global Disaster Alert and Coordination System, GDACS"
"""

import requests
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DisasterAlert:
    """Structured representation of a single GDACS disaster event."""
    event_id: int
    event_type: str            # "FL" (flood), "TC" (cyclone), "EQ" (earthquake), "VO" (volcano)
    name: str
    description: str
    alert_level: str           # "Green", "Orange", "Red"
    alert_score: float         # 0–3
    country: str
    iso3: str
    latitude: float
    longitude: float
    from_date: str
    to_date: str
    glide: str                 # GLIDE disaster ID (e.g. "FL-2025-000171-IND")
    severity_text: str
    source: str                # e.g. "GLOFAS", "JTWC"
    report_url: str
    affected_countries: list[str] = field(default_factory=list)

    @property
    def severity_multiplier(self) -> float:
        """Map GDACS alert level to a victim severity multiplier."""
        return {"Green": 0.5, "Orange": 1.0, "Red": 1.5}.get(self.alert_level, 1.0)

    @property
    def is_flood(self) -> bool:
        return self.event_type == "FL"


class DisasterAlertService:
    """Queries the GDACS API for live disaster alerts."""

    BASE_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.alerts: list[DisasterAlert] = []
        self.last_query_time: Optional[datetime] = None

    # ------------------------------------------------------------------ #
    #  Query
    # ------------------------------------------------------------------ #

    def fetch_alerts(
        self,
        event_type: str = "FL",
        country_iso3: str = "IND",
        limit: int = 10,
    ) -> list[DisasterAlert]:
        """
        Fetch recent disaster alerts from GDACS.

        Parameters
        ----------
        event_type : str
            "FL" (flood), "TC" (tropical cyclone), "EQ" (earthquake), "VO" (volcano).
        country_iso3 : str
            ISO-3166 alpha-3 country code (e.g. "IND" for India).
        limit : int
            Max number of events to return.

        Returns
        -------
        List of DisasterAlert objects, sorted by alert_score descending.
        """
        print(f"\n🚨 Querying GDACS for live {event_type} alerts in {country_iso3} …")

        try:
            resp = requests.get(
                self.BASE_URL,
                params={
                    "eventtype": event_type,
                    "country": country_iso3,
                    "limit": limit,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  ⚠ GDACS API query failed: {e}")
            self.alerts = []
            return self.alerts

        features = data.get("features", [])
        self.alerts = []

        for feat in features:
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [0, 0])

            # Only include events matching the requested type
            if props.get("eventtype", "") != event_type:
                continue

            alert = DisasterAlert(
                event_id=props.get("eventid", 0),
                event_type=props.get("eventtype", ""),
                name=props.get("name", "Unknown"),
                description=props.get("htmldescription", ""),
                alert_level=props.get("alertlevel", "Green"),
                alert_score=props.get("alertscore", 0),
                country=props.get("country", ""),
                iso3=props.get("iso3", ""),
                latitude=float(coords[1]) if len(coords) > 1 else 0.0,
                longitude=float(coords[0]) if len(coords) > 0 else 0.0,
                from_date=props.get("fromdate", ""),
                to_date=props.get("todate", ""),
                glide=props.get("glide", ""),
                severity_text=props.get("severitydata", {}).get("severitytext", ""),
                source=props.get("source", ""),
                report_url=props.get("url", {}).get("report", ""),
                affected_countries=[
                    c.get("countryname", "") for c in props.get("affectedcountries", [])
                ],
            )
            self.alerts.append(alert)

        # Sort by alert score descending (most severe first)
        self.alerts.sort(key=lambda a: a.alert_score, reverse=True)
        self.last_query_time = datetime.utcnow()

        if self.alerts:
            print(f"  ✅ Found {len(self.alerts)} {event_type} alert(s):")
            for a in self.alerts[:3]:
                print(f"     • [{a.alert_level}] {a.name} (score {a.alert_score}) — {a.from_date[:10]}")
        else:
            print(f"  ℹ No active {event_type} alerts found for {country_iso3}.")

        return self.alerts

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def get_most_severe(self) -> Optional[DisasterAlert]:
        """Return the highest-scoring alert, or None."""
        return self.alerts[0] if self.alerts else None

    def get_severity_multiplier(self) -> float:
        """
        Return a severity multiplier derived from the most severe active alert.
        Falls back to 1.0 (moderate) if no alerts are available.
        """
        alert = self.get_most_severe()
        if alert:
            return alert.severity_multiplier
        return 1.0

    def get_dashboard_summary(self) -> dict:
        """
        Return a dict of headline data for display in the Streamlit sidebar.
        """
        alert = self.get_most_severe()
        if alert is None:
            return {
                "has_alert": False,
                "alert_level": "None",
                "event_name": "No active alerts",
                "severity_text": "",
                "date_range": "",
                "source": "",
                "glide": "",
                "report_url": "",
                "severity_multiplier": 1.0,
                "total_alerts": 0,
            }
        return {
            "has_alert": True,
            "alert_level": alert.alert_level,
            "event_name": alert.name,
            "severity_text": alert.severity_text,
            "date_range": f"{alert.from_date[:10]} → {alert.to_date[:10]}",
            "source": alert.source,
            "glide": alert.glide,
            "report_url": alert.report_url,
            "severity_multiplier": alert.severity_multiplier,
            "total_alerts": len(self.alerts),
        }
