from flask import Flask, jsonify, render_template, request
import datetime
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")


# Configuration and Data Models


@dataclass
class EconomicStatus:
    """Economic status configuration"""
    name: str
    power_on_multiplier: float  # Multiplier for power-on duration
    power_off_multiplier: float  # Multiplier for power-off duration
    description: str


# Economic status definitions
ECONOMIC_STATUSES = {
    "good": EconomicStatus(
        name="Good",
        power_on_multiplier=1.2,  # 20% more power-on time
        power_off_multiplier=0.8,  # 20% less power-off time
        description="Strong economy - Better power availability"
    ),
    "moderate": EconomicStatus(
        name="Moderate",
        power_on_multiplier=1.0,  # Standard schedules
        power_off_multiplier=1.0,
        description="Stable economy - Standard power schedules"
    ),
    "poor": EconomicStatus(
        name="Poor",
        power_on_multiplier=0.8,  # 20% less power-on time
        power_off_multiplier=1.2,  # 20% more power-off time
        description="Economic challenges - Reduced power availability"
    ),
    "critical": EconomicStatus(
        name="Critical",
        power_on_multiplier=0.6,  # 40% less power-on time
        power_off_multiplier=1.4,  # 40% more power-off time
        description="Severe economic crisis - Significantly reduced power"
    )
}

# Default economic status (can be changed via API)
current_economic_status = "moderate"

# Municipality and area data
MUNICIPALITIES = [
    {"name": "Luanda", "areas": ["Maianga",
                                 "Ingombota", "Samba", "Rangel", "Alvalade"]},
    {"name": "Belas", "areas": [
        "Talatona", "Futungo de Belas", "Morro Bento", "Benfica", "Camama"]},
    {"name": "Cacuaco", "areas": ["Cacuaco Central", "Sequele", "Kicolo"]},
    {"name": "Viana", "areas": ["Zango 1", "Zango 2", "Zango 3",
                                "Zango 4", "Vila de Viana", "Estalagem", "Vila Chinesa"]},
    {"name": "Cazenga", "areas": [
        "Cazenga Central", "Hoji-ya-Henda", "Tala-Hady"]},
    {"name": "Kilama Kiaxi", "areas": ["Kilamba City", "Sapu", "Golfe"]},
    {"name": "Icolo e Bengo", "areas": ["Catete", "Bom Jesus"]},
    {"name": "Quicama", "areas": ["Muxima", "Cabo Ledo", "Barra do Cuanza"]}
]

# Base schedule templates (used as reference for generating dynamic schedules)
BASE_SCHEDULES = {
    "Luanda": {
        "Maianga": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Ingombota": [
            {"start": "06:00", "end": "10:00", "status": "Power on"},
            {"start": "10:00", "end": "13:00", "status": "Power off"},
            {"start": "13:00", "end": "16:00", "status": "Power on"},
            {"start": "16:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "23:00", "status": "Power on"},
            {"start": "23:00", "end": "06:00", "status": "Power off"},
        ],
        "Samba": [
            {"start": "06:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Rangel": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Alvalade": [
            {"start": "06:00", "end": "10:00", "status": "Power on"},
            {"start": "10:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "16:00", "status": "Power on"},
            {"start": "16:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "23:00", "status": "Power on"},
            {"start": "23:00", "end": "06:00", "status": "Power off"},
        ],
    },
    "Belas": {
        "Talatona": [
            {"start": "06:00", "end": "10:00", "status": "Power on"},
            {"start": "10:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "16:00", "status": "Power on"},
            {"start": "16:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "23:00", "status": "Power on"},
            {"start": "23:00", "end": "06:00", "status": "Power off"},
        ],
        "Futungo de Belas": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Morro Bento": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Benfica": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Camama": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
    },
    "Cacuaco": {
        "Cacuaco Central": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Sequele": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Kicolo": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
    },
    "Viana": {
        "Zango 1": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Zango 2": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Zango 3": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Zango 4": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "06:00", "status": "Power off"},
        ],
        "Vila de Viana": [
            {"start": "05:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "16:00", "status": "Power off"},
            {"start": "16:00", "end": "21:00", "status": "Power on"},
            {"start": "21:00", "end": "05:00", "status": "Power off"},
        ],
        "Estalagem": [
            {"start": "04:00", "end": "07:00", "status": "Power on"},
            {"start": "07:00", "end": "10:00", "status": "Power off"},
            {"start": "10:00", "end": "13:00", "status": "Power on"},
            {"start": "13:00", "end": "15:00", "status": "Power off"},
            {"start": "15:00", "end": "20:00", "status": "Power on"},
            {"start": "20:00", "end": "04:00", "status": "Power off"},
        ],
        "Vila Chinesa": [
            {"start": "05:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "16:00", "status": "Power off"},
            {"start": "16:00", "end": "21:00", "status": "Power on"},
            {"start": "21:00", "end": "05:00", "status": "Power off"},
        ],
    },
    "Cazenga": {
        "Cazenga Central": [
            {"start": "05:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "16:00", "status": "Power off"},
            {"start": "16:00", "end": "21:00", "status": "Power on"},
            {"start": "21:00", "end": "05:00", "status": "Power off"},
        ],
        "Hoji-ya-Henda": [
            {"start": "06:00", "end": "10:00", "status": "Power on"},
            {"start": "10:00", "end": "13:00", "status": "Power off"},
            {"start": "13:00", "end": "16:00", "status": "Power on"},
            {"start": "16:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "23:00", "status": "Power on"},
            {"start": "23:00", "end": "06:00", "status": "Power off"},
        ],
        "Tala-Hady": [
            {"start": "05:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "16:00", "status": "Power off"},
            {"start": "16:00", "end": "21:00", "status": "Power on"},
            {"start": "21:00", "end": "05:00", "status": "Power off"},
        ],
    },
    "Kilama Kiaxi": {
        "Kilamba City": [
            {"start": "05:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "16:00", "status": "Power off"},
            {"start": "16:00", "end": "21:00", "status": "Power on"},
            {"start": "21:00", "end": "05:00", "status": "Power off"},
        ],
        "Sapu": [
            {"start": "06:00", "end": "10:00", "status": "Power on"},
            {"start": "10:00", "end": "13:00", "status": "Power off"},
            {"start": "13:00", "end": "16:00", "status": "Power on"},
            {"start": "16:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "23:00", "status": "Power on"},
            {"start": "23:00", "end": "06:00", "status": "Power off"},
        ],
        "Golfe": [
            {"start": "07:00", "end": "11:00", "status": "Power on"},
            {"start": "11:00", "end": "14:00", "status": "Power off"},
            {"start": "14:00", "end": "17:00", "status": "Power on"},
            {"start": "17:00", "end": "19:00", "status": "Power off"},
            {"start": "19:00", "end": "24:00", "status": "Power on"},
            {"start": "24:00", "end": "07:00", "status": "Power off"},
        ],
    },
    "Icolo e Bengo": {
        "Catete": [
            {"start": "05:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "05:00", "status": "Power off"},
        ],
        "Bom Jesus": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "23:00", "status": "Power on"},
            {"start": "23:00", "end": "06:00", "status": "Power off"},
        ],
    },
    "Quicama": {
        "Muxima": [
            {"start": "04:00", "end": "07:00", "status": "Power on"},
            {"start": "07:00", "end": "10:00", "status": "Power off"},
            {"start": "10:00", "end": "13:00", "status": "Power on"},
            {"start": "13:00", "end": "16:00", "status": "Power off"},
            {"start": "16:00", "end": "21:00", "status": "Power on"},
            {"start": "21:00", "end": "04:00", "status": "Power off"},
        ],
        "Cabo Ledo": [
            {"start": "05:00", "end": "08:00", "status": "Power on"},
            {"start": "08:00", "end": "11:00", "status": "Power off"},
            {"start": "11:00", "end": "14:00", "status": "Power on"},
            {"start": "14:00", "end": "17:00", "status": "Power off"},
            {"start": "17:00", "end": "22:00", "status": "Power on"},
            {"start": "22:00", "end": "05:00", "status": "Power off"},
        ],
        "Barra do Cuanza": [
            {"start": "06:00", "end": "09:00", "status": "Power on"},
            {"start": "09:00", "end": "12:00", "status": "Power off"},
            {"start": "12:00", "end": "15:00", "status": "Power on"},
            {"start": "15:00", "end": "18:00", "status": "Power off"},
            {"start": "18:00", "end": "23:00", "status": "Power on"},
            {"start": "23:00", "end": "06:00", "status": "Power off"},
        ],
    },
}


# Schedule Generation Logic


def time_to_minutes(time_str: str) -> int:
    """Convert time string (HH:MM) to minutes since midnight"""
    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to time string (HH:MM)"""
    hours = (minutes // 60) % 24
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def generate_schedule_for_area(municipality: str, area: str, economic_status: str) -> List[Dict]:
    """
    Generate a schedule for a specific area based on economic status.
    Adjusts power-on and power-off durations according to economic conditions.
    Maintains schedule continuity throughout the day.
    """
    if municipality not in BASE_SCHEDULES or area not in BASE_SCHEDULES[municipality]:
        return []

    if economic_status not in ECONOMIC_STATUSES:
        economic_status = "moderate"

    status_config = ECONOMIC_STATUSES[economic_status]
    base_schedule = BASE_SCHEDULES[municipality][area]
    adjusted_schedule = []

    # Start from the first slot's start time
    current_time_min = time_to_minutes(base_schedule[0]["start"])

    for slot in base_schedule:
        start_time_str = slot["start"]
        end_time_str = slot["end"]
        status = slot["status"]

        # Calculate original duration
        start_min = time_to_minutes(start_time_str)
        end_min = time_to_minutes(end_time_str)

        # Handle midnight crossover
        if end_min < start_min:
            end_min += 24 * 60

        original_duration = end_min - start_min

        # Apply multiplier based on status
        if status == "Power on":
            multiplier = status_config.power_on_multiplier
        else:
            multiplier = status_config.power_off_multiplier

        # Calculate new duration
        new_duration = int(original_duration * multiplier)

        # Ensure minimum duration of 30 minutes
        if new_duration < 30:
            new_duration = 30

        # Calculate new end time
        new_end_min = (current_time_min + new_duration) % (24 * 60)

        # Create adjusted slot
        adjusted_schedule.append({
            "start": minutes_to_time(current_time_min),
            "end": minutes_to_time(new_end_min),
            "status": status
        })

        # Move to next slot start (which is the end of current slot)
        current_time_min = new_end_min

    # Ensure the last slot wraps properly to the first slot's start
    if adjusted_schedule:
        first_start_min = time_to_minutes(adjusted_schedule[0]["start"])
        last_end_min = time_to_minutes(adjusted_schedule[-1]["end"])

        # If last end is before first start (or equal), it's already correct
        # If last end is after first start, we need to wrap it
        if last_end_min > first_start_min:
            # The last slot should end at the first slot's start (wrapping)
            # But we need to handle this in the status check logic instead
            pass

    return adjusted_schedule


def get_current_schedules() -> Dict:
    """Get all current schedules based on economic status"""
    schedules = {}
    for municipality in BASE_SCHEDULES:
        schedules[municipality] = {}
        for area in BASE_SCHEDULES[municipality]:
            schedules[municipality][area] = generate_schedule_for_area(
                municipality, area, current_economic_status
            )
    return schedules


# Power Status Logic


def get_current_power_status(municipality: str, area: str) -> str:
    """Get current power status for a specific area"""
    schedules = get_current_schedules()

    if municipality not in schedules or area not in schedules[municipality]:
        return "Unknown"

    current_time = datetime.datetime.now().time()
    area_schedule = schedules[municipality][area]

    for slot in area_schedule:
        start_time = datetime.datetime.strptime(slot["start"], "%H:%M").time()
        end_time = datetime.datetime.strptime(slot["end"], "%H:%M").time()

        # Handle time ranges that cross midnight
        if start_time > end_time:  # crosses midnight
            if current_time >= start_time or current_time < end_time:
                return slot["status"]
        else:  # normal time range
            if start_time <= current_time < end_time:
                return slot["status"]

    return "Unknown"


# Flask Routes


@app.route('/')
def index():
    """Main page displaying power schedule interface"""
    schedules = get_current_schedules()
    economic_status_info = ECONOMIC_STATUSES.get(
        current_economic_status, ECONOMIC_STATUSES["moderate"])

    return render_template(
        'index.html',
        municipalities=MUNICIPALITIES,
        economic_status=current_economic_status,
        economic_status_name=economic_status_info.name,
        economic_status_description=economic_status_info.description,
        available_statuses=list(ECONOMIC_STATUSES.keys())
    )


@app.route('/api/areas/<municipality>')
def get_areas(municipality):
    """API endpoint to get areas for a specific municipality"""
    for muni in MUNICIPALITIES:
        if muni["name"] == municipality:
            return jsonify(muni["areas"])
    return jsonify([])


@app.route('/api/schedule/<municipality>/<area>')
def get_schedule(municipality, area):
    """API endpoint to get schedule for specific municipality and area"""
    schedules = get_current_schedules()

    if municipality in schedules and area in schedules[municipality]:
        current_status = get_current_power_status(municipality, area)
        economic_status_info = ECONOMIC_STATUSES.get(
            current_economic_status, ECONOMIC_STATUSES["moderate"])

        return jsonify({
            "schedule": schedules[municipality][area],
            "current_status": current_status,
            "current_time": datetime.datetime.now().strftime("%H:%M"),
            "economic_status": current_economic_status,
            "economic_status_name": economic_status_info.name
        })
    return jsonify({"error": "Schedule not found"}), 404


@app.route('/api/economic-status', methods=['GET'])
def get_economic_status():
    """Get current economic status"""
    economic_status_info = ECONOMIC_STATUSES.get(
        current_economic_status, ECONOMIC_STATUSES["moderate"])
    return jsonify({
        "status": current_economic_status,
        "name": economic_status_info.name,
        "description": economic_status_info.description,
        "power_on_multiplier": economic_status_info.power_on_multiplier,
        "power_off_multiplier": economic_status_info.power_off_multiplier
    })


@app.route('/api/economic-status', methods=['POST'])
def update_economic_status():
    """Update economic status (regenerates all schedules)"""
    global current_economic_status

    data = request.get_json()
    new_status = data.get('status', '').lower()

    if new_status not in ECONOMIC_STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of: {list(ECONOMIC_STATUSES.keys())}"}), 400

    current_economic_status = new_status
    economic_status_info = ECONOMIC_STATUSES[current_economic_status]

    return jsonify({
        "message": "Economic status updated successfully",
        "status": current_economic_status,
        "name": economic_status_info.name,
        "description": economic_status_info.description,
        "schedules_regenerated": True
    })


@app.route('/schedule')
def schedule_page():
    """Display schedule for specific municipality and area"""
    municipality = request.args.get('municipality')
    area = request.args.get('area')

    if not municipality or not area:
        schedules = get_current_schedules()
        economic_status_info = ECONOMIC_STATUSES.get(
            current_economic_status, ECONOMIC_STATUSES["moderate"])
        return render_template(
            'index.html',
            municipalities=MUNICIPALITIES,
            economic_status=current_economic_status,
            economic_status_name=economic_status_info.name,
            economic_status_description=economic_status_info.description,
            available_statuses=list(ECONOMIC_STATUSES.keys()),
            error="Please select both municipality and area"
        )

    schedules = get_current_schedules()

    if municipality not in schedules or area not in schedules[municipality]:
        economic_status_info = ECONOMIC_STATUSES.get(
            current_economic_status, ECONOMIC_STATUSES["moderate"])
        return render_template(
            'index.html',
            municipalities=MUNICIPALITIES,
            economic_status=current_economic_status,
            economic_status_name=economic_status_info.name,
            economic_status_description=economic_status_info.description,
            available_statuses=list(ECONOMIC_STATUSES.keys()),
            error="Schedule not found for the selected location"
        )

    area_schedule = schedules[municipality][area]
    current_status = get_current_power_status(municipality, area)
    current_time = datetime.datetime.now().strftime("%H:%M")
    economic_status_info = ECONOMIC_STATUSES.get(
        current_economic_status, ECONOMIC_STATUSES["moderate"])

    return render_template(
        'index.html',
        municipalities=MUNICIPALITIES,
        selected_municipality=municipality,
        selected_area=area,
        schedule=area_schedule,
        current_status=current_status,
        current_time=current_time,
        economic_status=current_economic_status,
        economic_status_name=economic_status_info.name,
        economic_status_description=economic_status_info.description,
        available_statuses=list(ECONOMIC_STATUSES.keys())
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
