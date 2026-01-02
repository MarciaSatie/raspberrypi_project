### 📷 Smart Security & Monitoring System

IoT Camera Platform – Raspberry Pi 4

📌 Project Overview

This project is a Smart Security & Monitoring System built using a Raspberry Pi 4 and a camera module.
It is an IoT-based solution that captures real-world visual data, processes it locally, transmits it over a network, and displays it in a web-based application.

The system detects motion, captures images when activity is detected, and makes them available to users through a browser-based dashboard.
This simulates a real-world smart security product.

This project was developed as part of a college IoT & Computer Systems assignment and follows a full IoT architecture.

### Github project:
https://github.com/MarciaSatie/raspberrypi_project

### Render Website link:
https://raspberrypi-project.onrender.com

1. Any time you open a new terminal for this project, run:
source .venv/bin/activate


###🧱 IoT Architecture

### 🔍 System Layers
| Layer           | Implementation                          |
| --------------- | --------------------------------------- |
| **Sensor**      | Raspberry Pi Camera Module              |
| **Processing**  | Python + OpenCV for motion detection    |
| **Network**     | Wi-Fi using MQTT
| **Application** | Web dashboard (Flask + HTML/CSS/JS)     |

### 🛠 Technologies Used

Raspberry Pi 4
Raspberry Pi Camera
Python
Flask (Web Server & API)
HTML
MQTT