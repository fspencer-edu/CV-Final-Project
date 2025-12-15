#include <Arduino.h>
#include "esp_http_server.h"
#include "esp_camera.h"

httpd_handle_t camera_httpd = NULL;

// ================================
// Helper: send single JPEG frame
// ================================
esp_err_t send_frame_as_jpeg(httpd_req_t *req, framesize_t frame_size, int quality) {
  sensor_t *s = esp_camera_sensor_get();
  if (!s) return ESP_FAIL;

  // Store and update temporary parameters
  framesize_t old_size = s->status.framesize;
  int old_quality = s->status.quality;

  s->set_framesize(s, frame_size);
  s->set_quality(s, quality);
  delay(120);  // allow exposure to adapt

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  // Send the JPEG image directly
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);

  esp_camera_fb_return(fb);

  // Restore previous settings
  s->set_framesize(s, old_size);
  s->set_quality(s, old_quality);

  if (res == ESP_OK)
    Serial.printf("✅ JPEG sent: %u bytes\n", fb->len);
  else
    Serial.printf("⚠️ HTTP send error %d\n", res);

  return res;
}

// ================================
// MJPEG Streamer (continuous feed)
// ================================
static const char *_STREAM_CONTENT_TYPE = "multipart/x-mixed-replace; boundary=--frame";
static const char *_STREAM_BOUNDARY = "\r\n--frame\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\n\r\n";

esp_err_t stream_frames(httpd_req_t *req, framesize_t size, int quality) {
  sensor_t *s = esp_camera_sensor_get();
  s->set_framesize(s, size);
  s->set_quality(s, quality);
  delay(100);

  esp_err_t res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  // Large buffered chunk size (tunable)
  const size_t CHUNK_SIZE = 4096;

  while (true) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("⚠️ Frame capture failed");
      delay(50);
      continue;
    }

    // Send boundary marker
    res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    if (res != ESP_OK) {
      esp_camera_fb_return(fb);
      break;
    }

    // Send frame header
    res = httpd_resp_send_chunk(req, _STREAM_PART, strlen(_STREAM_PART));
    if (res != ESP_OK) {
      esp_camera_fb_return(fb);
      break;
    }

    // Send JPEG data in large chunks
    size_t remaining = fb->len;
    uint8_t *buf_ptr = fb->buf;
    while (remaining > 0) {
      size_t to_send = remaining > CHUNK_SIZE ? CHUNK_SIZE : remaining;
      res = httpd_resp_send_chunk(req, (const char *)buf_ptr, to_send);
      if (res != ESP_OK) break;
      buf_ptr += to_send;
      remaining -= to_send;
    }

    // Separate frames with CRLF
    if (res == ESP_OK)
      res = httpd_resp_send_chunk(req, "\r\n", 2);

    esp_camera_fb_return(fb);
    if (res != ESP_OK) break;

    delay(60); // Controls FPS: 30–80ms typical
  }

  return res;
}

// ================================
// Route Handlers
// ================================
static esp_err_t index_handler(httpd_req_t *req) {
  const char *msg =
    "ESP32-CAM API Endpoints:\n"
    "  /low-quality          → Single fast JPEG\n"
    "  /high-quality         → Single detailed JPEG\n"
    "  /ultra-quality        → Maximum resolution JPEG\n"
    "  /low-quality-stream   → MJPEG stream (low res)\n"
    "  /high-quality-stream  → MJPEG stream (high res)\n"
    "  /ultra-quality-stream → MJPEG stream (max res, slower)\n";
  httpd_resp_set_type(req, "text/plain");
  return httpd_resp_send(req, msg, strlen(msg));
}

// Single-frame endpoints
static esp_err_t low_quality_handler(httpd_req_t *req) {
  Serial.println("➡️ Low-quality frame requested");
  return send_frame_as_jpeg(req, FRAMESIZE_VGA, 25);  // 640x480 fast
}
static esp_err_t high_quality_handler(httpd_req_t *req) {
  Serial.println("➡️ High-quality frame requested");
  return send_frame_as_jpeg(req, FRAMESIZE_SVGA, 12); // 800x600 mid
}
static esp_err_t ultra_quality_handler(httpd_req_t *req) {
  Serial.println("🚀 Ultra-quality frame requested");
  return send_frame_as_jpeg(req, FRAMESIZE_UXGA, 8);  // 1600x1200 best
}

// Stream endpoints
static esp_err_t low_quality_stream_handler(httpd_req_t *req) {
  Serial.println("🎥 Low-quality stream started");
  return stream_frames(req, FRAMESIZE_VGA, 25);
}
static esp_err_t high_quality_stream_handler(httpd_req_t *req) {
  Serial.println("🎥 High-quality stream started");
  return stream_frames(req, FRAMESIZE_SVGA, 12);
}
static esp_err_t ultra_quality_stream_handler(httpd_req_t *req) {
  Serial.println("🎥 Ultra-quality stream started");
  return stream_frames(req, FRAMESIZE_UXGA, 8);
}

// ================================
// Start HTTP Server
// ================================
void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.max_uri_handlers = 12;

  httpd_uri_t index_uri   = { .uri="/",                    .method=HTTP_GET, .handler=index_handler };
  httpd_uri_t low_uri     = { .uri="/low-quality",         .method=HTTP_GET, .handler=low_quality_handler };
  httpd_uri_t high_uri    = { .uri="/high-quality",        .method=HTTP_GET, .handler=high_quality_handler };
  httpd_uri_t ultra_uri   = { .uri="/ultra-quality",       .method=HTTP_GET, .handler=ultra_quality_handler };
  httpd_uri_t low_stream  = { .uri="/low-quality-stream",  .method=HTTP_GET, .handler=low_quality_stream_handler };
  httpd_uri_t high_stream = { .uri="/high-quality-stream", .method=HTTP_GET, .handler=high_quality_stream_handler };
  httpd_uri_t ultra_stream= { .uri="/ultra-quality-stream",.method=HTTP_GET, .handler=ultra_quality_stream_handler };

  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &low_uri);
    httpd_register_uri_handler(camera_httpd, &high_uri);
    httpd_register_uri_handler(camera_httpd, &ultra_uri);
    httpd_register_uri_handler(camera_httpd, &low_stream);
    httpd_register_uri_handler(camera_httpd, &high_stream);
    httpd_register_uri_handler(camera_httpd, &ultra_stream);

    Serial.println("🌐 ESP32-CAM API server started:");
    Serial.println("   • /low-quality");
    Serial.println("   • /high-quality");
    Serial.println("   • /ultra-quality");
    Serial.println("   • /low-quality-stream");
    Serial.println("   • /high-quality-stream");
    Serial.println("   • /ultra-quality-stream");
  } else {
    Serial.println("❌ Failed to start server!");
  }
}
