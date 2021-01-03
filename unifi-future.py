from unifi_video import UnifiVideoAPI

# https://github.com/yuppity/unifi-video-api
# https://marcz.dk/2019/08/02/human-detection-with-ubiquitis-unifi-video-and-python/

if __name__ == '__main__':
    # Use API key (can be set per user in Unifi NVR user settings)
    uva = UnifiVideoAPI(api_key='r4ezaqqHS9uMo73IA4HNiIHKVU9y1bYn', addr='192.168.0.2')

    # List all cameras UniFi Video is aware of
    for camera in uva.cameras:
        print(camera)

    # for camera in uva.active_cameras:
    #     camera.snapshot()
    for rec in uva.recordings:
        print(rec)

