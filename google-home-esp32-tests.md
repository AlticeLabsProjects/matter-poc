# ESP32 RGB Lighting App Testes
## Commissioning using Google Home App
* Adding the ESP32 Light App was done successfully.
* There are some issues when removing the device from previous fabrics. Just removing from the App is not enough, we need to erase the flash from the device itself.

## Testing the device inside the home
* The device works from Google App when nest hub or nest mini are turned on.
* Apparently, google home mini is not a contoller, because when turned on and the others are turned off, cannot control the device inside of the home
* If we turn off all Google Hubs (the 3 ones from the previous step) the device does now work anymore

## Testing the device out of home
* The device works from Google App even when I'm outside of the home.
* For that to work, we need to have at least one active controller in the house. In this case it only works with nest mini or nest hub display
* Apparently, google home mini is not a contoller, because when turned on and the others are turned off, cannot control the device outside of the home

## If we turn off all Google Hubs (the 3 ones from the previous step) 
* Cannot control the device anymore from outside of the home.
* Also cannot control the device from inside the home

## Remove the internet access from Fiber Gateway (remove the fiber)
* Couldn't control the device in any circunstance.
* All Hubs are turned on but still cannot control the device.

### Considerations
* We can conclude that Google allows remote control of the device if we have valid controllers running inside the house, in this case, the nest mini and the hub display
* Not all Hubs work as controller. Could not control using Google Home Mini.
* Matter does not work without internet from the Router. Needs more testing!

