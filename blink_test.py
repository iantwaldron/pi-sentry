from gpiozero import LED
from time import sleep

# Change GPIO pin as needed - using GPIO 17 (pin 11)
led = LED(17)

print("Blinking LED on GPIO 17 - Ctrl+C to stop")

while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
