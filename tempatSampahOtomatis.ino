#include <Servo.h>

#define SERVO_PIN 10
Servo myServo;

void setup() {
  myServo.attach(SERVO_PIN);
  myServo.write(0); // Tutup tutup sampah
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();
    if (signal == '1') {
      myServo.write(90); // Buka tutup sampah
      delay(3000); // Tunggu 3 detik (masukkan sampah)
      myServo.write(0); // Tutup kembali
      delay(500);
      Serial.println("DONE"); // Kirim sinyal ke Python bahwa sudah selesai
    }
  }
  delay(100);
}