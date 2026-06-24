#include <Adafruit_GFX.h>
#include <MCUFRIEND_kbv.h>

MCUFRIEND_kbv tft;

#define MOTION_PIN 53
#define SPEAKER_PIN 49

#define BLACK 0x0000
#define WHITE 0xFFFF
#define RED 0xF800
#define GREEN 0x07E0
#define BLUE 0x001F

int displayedMotionState = -1;

unsigned long lastMotionSeenTime = 0;
const unsigned long motionHoldTime = 250;

void setup() {
  Serial.begin(9600);

  pinMode(MOTION_PIN, INPUT);
  pinMode(SPEAKER_PIN, OUTPUT);

  uint16_t ID = tft.readID();

  tft.begin(ID);
  tft.setRotation(1);
  tft.fillScreen(BLACK);
}

void loop() {
  int sensorValue = digitalRead(MOTION_PIN);

  bool rawMotion = (sensorValue == HIGH);

  if (rawMotion) {
    lastMotionSeenTime = millis();
  }

  bool motionNow = (millis() - lastMotionSeenTime < motionHoldTime);

  if ((int)motionNow != displayedMotionState) {
    displayedMotionState = motionNow;

    if (motionNow) {
      showMotionSymbol();
      tone(SPEAKER_PIN, 2000);
      Serial.println("Motion detected");
    } else {
      showNoMotionSymbol();
      noTone(SPEAKER_PIN);
      Serial.println("No motion");
    }
  }
}

void showNoMotionSymbol() {
  tft.fillScreen(GREEN);

  int cx = tft.width() / 2;
  int cy = tft.height() / 2;
  int r = 95;

  tft.fillCircle(cx, cy, r, BLUE);

  drawThickLine(cx - 45, cy + 10, cx - 5, cy + 50, WHITE, 6);
  drawThickLine(cx - 5, cy + 50, cx + 55, cy - 35, WHITE, 6);
}

void showMotionSymbol() {
  tft.fillScreen(RED);

  int cx = tft.width() / 2;
  int cy = tft.height() / 2;
  int r = 95;

  tft.fillCircle(cx, cy, r, BLACK);

  drawPersonIcon(cx, cy, WHITE);

  drawThickLine(cx - 65, cy - 65, cx + 65, cy + 65, WHITE, 6);
}

void drawPersonIcon(int cx, int cy, uint16_t color) {
  tft.fillCircle(cx, cy - 35, 16, color);

  tft.fillRect(cx - 8, cy - 15, 16, 45, color);

  drawThickLine(cx - 28, cy - 5, cx + 28, cy - 5, color, 3);

  drawThickLine(cx, cy + 30, cx - 24, cy + 65, color, 3);
  drawThickLine(cx, cy + 30, cx + 24, cy + 65, color, 3);
}

void drawThickLine(int x1, int y1, int x2, int y2, uint16_t color, int thickness) {
  for (int i = -thickness; i <= thickness; i++) {
    tft.drawLine(x1 + i, y1, x2 + i, y2, color);
    tft.drawLine(x1, y1 + i, x2, y2 + i, color);
  }
}