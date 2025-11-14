Angola Power Schedule - ENE
A Flask-based web application that provides real-time power outage schedules for various municipalities and areas across Angola. The system dynamically adjusts power schedules based on economic conditions, helping residents plan around power availability.
Features

Real-time Power Status: View current power status for your specific location
Dynamic Schedule Generation: Schedules automatically adjust based on economic conditions
Economic Status Control: Four economic statuses that affect power availability:

Good: 20% more power-on time, 20% less power-off time
Moderate: Standard schedules
Poor: 20% less power-on time, 20% more power-off time
Critical: 40% less power-on time, 40% more power-off time


Comprehensive Coverage: 8 municipalities with 40+ areas
Responsive Design: Mobile-friendly interface with Bootstrap dark theme
Live Updates: Current time display and automatic status calculation

Coverage Areas
Municipalities & Areas

Luanda: Maianga, Ingombota, Samba, Rangel, Alvalade
Belas: Talatona, Futungo de Belas, Morro Bento, Benfica, Camama
Cacuaco: Cacuaco Central, Sequele, Kicolo
Viana: Zango 1-4, Vila de Viana, Estalagem, Vila Chinesa
Cazenga: Cazenga Central, Hoji-ya-Henda, Tala-Hady
Kilama Kiaxi: Kilamba City, Sapu, Golfe
Icolo e Bengo: Catete, Bom Jesus
Quicama: Muxima, Cabo Ledo, Barra do Cuanza

Installation
Prerequisites

Python 3.11+
pip

Setup

Clone the repository:

bashgit clone https://github.com/yourusername/angola-power-schedule.git
cd angola-power-schedule

Install dependencies:

bashpip install -r requirements.txt

Set environment variables (optional):

bashexport SESSION_SECRET="your-secret-key"

Run the application:

bashpython app.py

Access the application at http://localhost:5000

Usage
Web Interface

Select your Municipality from the dropdown
Select your Area (options update based on municipality)
Click View Schedule to see the power schedule
View current power status and complete daily schedule

Economic Status Control
Administrators can adjust the economic status to regenerate all schedules:

Navigate to the Economic Status Control section
Select a new status from the dropdown
Click Update Status & Regenerate Schedules
All schedules are automatically recalculated

API Endpoints
Get Areas for Municipality
httpGET /api/areas/<municipality>
Get Schedule for Area
httpGET /api/schedule/<municipality>/<area>
Response:
json{
  "schedule": [...],
  "current_status": "Power on",
  "current_time": "14:30",
  "economic_status": "moderate",
  "economic_status_name": "Moderate"
}
Get Economic Status
httpGET /api/economic-status
Update Economic Status
httpPOST /api/economic-status
Content-Type: application/json

{
  "status": "good"
}
Technology Stack

Backend: Flask (Python)
Frontend: Bootstrap 5 (Dark Theme), Font Awesome
Styling: Custom CSS
JavaScript: Vanilla JS for dynamic interactions

Project Structure
angola-power-schedule/
├── app.py                  # Main Flask application
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── custom.css     # Custom styles
│   └── js/
│       └── app.js         # Client-side JavaScript
├── pyproject.toml         # Project dependencies
└── README.md              # This file
How It Works

Base Schedules: Predefined power schedules for each area
Economic Multipliers: Applied to power-on and power-off durations
Dynamic Generation: Schedules recalculated based on current economic status
Real-time Status: Current power status determined by comparing local time with generated schedules

Contributing
Contributions are welcome! Please follow these steps:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
