
#include "esp_camera.h"

#define CAM_PIN_PWDN    32 //power down is not used
#define CAM_PIN_RESET   -1 //software reset will be performed
#define CAM_PIN_XCLK     0
#define CAM_PIN_SIOD    26
#define CAM_PIN_SIOC    27

#define CAM_PIN_D7      35
#define CAM_PIN_D6      34
#define CAM_PIN_D5      39
#define CAM_PIN_D4      36
#define CAM_PIN_D3      21
#define CAM_PIN_D2      19
#define CAM_PIN_D1      18
#define CAM_PIN_D0       5
#define CAM_PIN_VSYNC   25
#define CAM_PIN_HREF    23
#define CAM_PIN_PCLK    22


static const camera_config_t camera_config = {
    .pin_pwdn  = CAM_PIN_PWDN,
    .pin_reset = CAM_PIN_RESET,
    .pin_xclk = CAM_PIN_XCLK,
    .pin_sscb_sda = CAM_PIN_SIOD,
    .pin_sscb_scl = CAM_PIN_SIOC,

    .pin_d7 = CAM_PIN_D7,
    .pin_d6 = CAM_PIN_D6,
    .pin_d5 = CAM_PIN_D5,
    .pin_d4 = CAM_PIN_D4,
    .pin_d3 = CAM_PIN_D3,
    .pin_d2 = CAM_PIN_D2,
    .pin_d1 = CAM_PIN_D1,
    .pin_d0 = CAM_PIN_D0,
    .pin_vsync = CAM_PIN_VSYNC,
    .pin_href = CAM_PIN_HREF,
    .pin_pclk = CAM_PIN_PCLK,

    .xclk_freq_hz = 20000000,
    .ledc_timer = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG,
    .frame_size = FRAMESIZE_CIF,

    .jpeg_quality = 10,
    .fb_count = 1
};


char metadataBuf[255] = {0};

char buf[10000] = {0};
int buflen = 0;

void send_photo()
{
    camera_fb_t* fb = esp_camera_fb_get();

    memset(metadataBuf, 0, 255);
    sprintf(metadataBuf, "\nW: %d\nH: %d\nL: %d\n", fb->width, fb->height, fb->len);

    memset(buf, 0, 10000);
    memcpy(buf, fb->buf, fb->len);
    buflen = fb->len;

    esp_camera_fb_return(fb);

    Serial.write(metadataBuf, 255);
    Serial.write(buf, buflen);
}

void setup()
{
    Serial.begin(256000);

    esp_err_t initError = esp_camera_init(&camera_config);
    if(initError != ESP_OK)
    {
        Serial.printf("Initialization failed. Error code: 0x%x\n", initError);
        return;
    }

    sensor_t *s = esp_camera_sensor_get();

    s->set_brightness(s, 0);
    s->set_contrast(s, 0);
    s->set_saturation(s, 0);
    s->set_special_effect(s, 0);
    s->set_whitebal(s, 1);
    s->set_exposure_ctrl(s, 1);
    s->set_gain_ctrl(s, 1);

    s->set_awb_gain(s, 1);

    s->set_wb_mode(s, 0);
    s->set_ae_level(s, 2);

    s->set_dcw(s, 1);
    s->set_wpc(s, 1);
    
    s->set_raw_gma(s, 1);
    s->set_lenc(s, 1);
}

void loop()
{
    if(Serial.available())
    {
        while(Serial.available()) Serial.read();
        send_photo();
    }
    delay(10);
}