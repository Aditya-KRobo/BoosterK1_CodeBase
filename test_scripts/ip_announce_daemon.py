#! /usr/bin/env python3

import socket
import pyttsx3

def get_wifi_ip():
    """Gets the current WiFi IP address."""
    try:
        # Create a socket to connect to an external address (no internet needed)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unable to find IP"

def speak_text(text):
    """Speaks the provided text."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    ip_address = get_wifi_ip()
    print(f"IP Address: {ip_address}")
    
    # Speak the IP address
    speak_text(f"Your WiFi IP address is {ip_address}")

