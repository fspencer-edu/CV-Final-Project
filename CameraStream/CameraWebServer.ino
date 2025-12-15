#include "esp_camera.h"
#include <WiFi.h>

// ===========================
// Select camera model in board_config.h
// ===========================
#include "board_config.h"

// ===========================
// Enter your WiFi credentials
// ===========================
const char* ssid = "Eero";           // your WiFi SSID
const char* password = "Lilydog2!";  // your WiFi password

void startCameraServer();
void setupLedFlash();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
  config.frame_size   = FRAMESIZE_VGA;        // 640x480
  config.jpeg_quality = 12;                   // moderate compression
  config.fb_count     = 2;                    // use two frame buffers
  config.grab_mode    = CAMERA_GRAB_LATEST;   // skip old frames
  config.fb_location  = CAMERA_FB_IN_PSRAM;
} else {
  config.frame_size   = FRAMESIZE_QVGA;
  config.jpeg_quality = 20;
  config.fb_count     = 2;                    // double-buffer
  config.fb_location  = CAMERA_FB_IN_DRAM;
}



  // --- Initialize camera ---
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return;
  }

  // --- Optional tuning ---
  sensor_t *s = esp_camera_sensor_get();
  s->set_dcw(s, 0);       // disable downsampling
  s->set_lenc(s, 1);      // enable lens correction for better sharpness
  s->set_raw_gma(s, 1);   // enable gamma correction for better contrast
  s->set_brightness(s, 1);
  s->set_saturation(s, -1);
  s->set_vflip(s, 0);
  s->set_hmirror(s, 0);
  // --- Connect Wi-Fi ---
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  WiFi.setTxPower(WIFI_POWER_19_5dBm);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println("\n✅ Wi-Fi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // --- Start webserver ---
  startCameraServer();

  Serial.print("Camera stream ready → http://");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Do nothing. Everything is done in another task by the web server
  delay(5);
}
