import json
from haversine import haversine, Unit
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="clinic_locator")


def get_coordinates(query):
    """Geocode a query like postal code, city or address"""
    try:
        location = geolocator.geocode(query)
        if location:
            return (location.latitude, location.longitude)
    except:
        pass
    return None


def find_nearest_by_postal(postal_code, top_n=3):

    with open("app/datasets/new_ivf_clinic.json", "r", encoding="utf-8") as f:
        clinics = json.load(f)
    base_clinic = next(
        (c for c in clinics if str(c.get("Postal")) == str(postal_code)), None
    )

    if (
        base_clinic
        and base_clinic.get("Latitude") is not None
        and base_clinic.get("Longitude") is not None
    ):
        base_loc = (base_clinic["Latitude"], base_clinic["Longitude"])
    else:

        base_loc = get_coordinates(postal_code)
        if not base_loc:
            return []

    results = []
    seen_names = set()
    for clinic in clinics:
        lat, lon = clinic.get("Latitude"), clinic.get("Longitude")
        name = clinic.get("Clinic Name")
        address = clinic.get("Address")
        if lat is None or lon is None or address in seen_names:
            continue  # skip null coordinates or duplicates
        dist = haversine(base_loc, (lat, lon), unit=Unit.KILOMETERS)
        results.append(
            {
                "Clinic Name": name,
                "City": clinic.get("City"),
                "State": clinic.get("State"),
                "Address": clinic.get("Address"),
                "Postal": clinic.get("Postal"),
                "Distance_km": round(dist, 2),
            }
        )
        seen_names.add(address)  # mark this clinic as added

    # Sort and return top_n nearest
    results = sorted(results, key=lambda x: x["Distance_km"])[:top_n]
    return results
