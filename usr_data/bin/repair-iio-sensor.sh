# Alles stoppen, was den Sensor berühren könnte
sudo systemctl stop iio-sensor-proxy
# Das ganze HID-Subsystem für Sensoren neu laden
sudo modprobe -r hid_sensor_accel_3d
sudo modprobe -r hid_sensor_gyro_3d
sudo modprobe -r hid_sensor_hub
sleep 2
sudo modprobe hid_sensor_hub
sudo modprobe hid_sensor_accel_3d
# Jetzt erst den Proxy wieder an
sudo systemctl start iio-sensor-proxy