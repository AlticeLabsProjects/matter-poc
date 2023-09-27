## Matter Architecture

- the Mobile App should use local interfaces when the mobile phone is connected to the local residential network 
- the API used in the local interface should be the same as the one used for remote control ie the mobile phone is not connected to the local residential network


![](Matter%20with%20HomeBot.png)

**HomeBot features**

Functionalities that are currently provided by HomeBot:

- User channel interaction API: Interface for integration with user channels, like voice assistants, assuring bidirectional communication if necessary (Not used, to be confirmed)
- Backoffice API: Interface to support backoffice Portal and operational tools - > to confirm if this is used with the new opco portal
- Device Management
- Home & Customers Inventory: knowledge base for all customers, homes and home objects including rooms and devices
- Devices & Services Inventory: knowledge base for device management, storing managed devices and services supported by them
- Home Config Manager: executes actions on home inventory objects, and knows how to map activities of the scenario into concrete actions on devices
- Device Config Manager: executes actions on devices
- Automation: Manages and executes scenarios, and executes customer intents, translating them into concrete actions on devices or home objects
- Analytics: Stores and processes events and performance indicators
- Multiprotocol Adaptation Layer: integrates with devices or 3rd party clouds.
  -	Command Executor: Issues commands to devices or 3rd party clouds
  -	Event Collector: Receives events from devices or 3rd party clouds
  - Event Handler: Filters relevant events and forwards them to the appropriate modules on the platform

- IP Cam Security manager with logic to handle WiFi IP Cameras as a security device
- Security Emergency Contacts management
- Alarm Notification handlers with different notification channels including SMS, Email, Voice and Push Notifications, using different emergency contacts managed by the end-user
- Firmware Management

**Manager**


