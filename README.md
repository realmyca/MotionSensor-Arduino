# MotionSensor-Arduino
Arduino device that updates a TFT display and beeps when motion is detected.

I built this project using an Arduino Mega, a 3.5" TFT LCD shield, a motion sensor, and a speaker to create a simple motion detection alert system.
When no motion is detected, the screen shows a green background with a check mark. When motion is detected, the screen changes to a red warning display and the speaker turns on.
I had help from my dad and AI while configuring and coding the project.

Here are some useful links vv

Library functions:
-> Adafruit-GFX-Library: https://github.com/adafruit/Adafruit-GFX-Library/blob/master/Adafruit_GFX.h

-> MCUFRIEND_kbv: https://github.com/prenticedavid/MCUFRIEND_kbv/blob/master/MCUFRIEND_kbv.h

-> Arduino stuff: https://docs.arduino.cc/learn/programming/reference/

Hardware I used:
-> Arduino Mega (I used a knockoff brand but heres the one from Arduino): https://store-usa.arduino.cc/products/arduino-mega-2560-rev3

-> speaker: https://www.seeedstudio.com/Grove-Speaker-p-1445.html

-> Motion sensor: https://www.seeedstudio.com/Grove-Adjustable-PIR-Motion-Sensor.html

-> 3.5" TFT LCD Shield: https://www.buydisplay.com/arduino-3-5-tft-lcd-touch-shield-serial-spi-example-for-mega-due


Comments:
-> If you plan on copying what I did, I had speaker on pin 49 and motion sensor on pin 53. Also remember to connect 5V pin and GND pin (the ones on the vertical side) onto a breadboard cause the screen uses 90% of the board
-> You can change the volume of the speaker with a small screwdriver (turn the white part)
