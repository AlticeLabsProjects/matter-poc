# Tuya Bulb
## Commissioning using Google Home App
* Trying to add a Tuya Bulb using Google Home result in a "Not a Matter-certified device".

## Commissioning using Home Assistant
* Added sucessfully using HASS.
* The control does not work 100% of the times. There are some missing on/off events and sometimes it flushes all events at once.

## Commissioning using Tuya
* Added sucessfully using Tuya.
* The control does not work 100% of the times. There are some missing on/off events. It works better then using HASS.
* Turned off WiFi and the Bulb went Offline and it didn't recover.
* Turned on WiFi and the Bulb went online again.

## Commissioning using Apple HomeKit
* Trying to add a Tuya Bulb using Apple HomeKit take A LOT of time in the "Connecting..." process, and after like 3 minutes, result in a "Accessory Noy Found".
* Resseting the Bulb, switching off and on the lamp 5 times, and after a very long wait, result in a different error, "Unable to Add Accessory - Pairing with accessory failed.".

### Considerations
In my acknowledge about chip-tool, and looking at the present vendor and product id of the Tuya Bulb in Home Assistant, Tuya is using project-chip/connectedhomeip, the same we are using on the ESP32 device, but maybe with some modifications, because the commissioning proccess works great with Espressif.
