# Identificação de dispositivos Matter

## Device Types

| Name | Hex | Dec |
| --- | --- | --- |
| Root Node | 0x00000016 | 22 |
| Plug | 0x0000010A | 266 |
| Blub | 0x0000010D | 269 |

## Clusters

| Cluster | Hex | Dec |
| --- | --- | --- |
| OnOff | 0x00000006 | 6 |
| LevelControl | 0x00000008 | 8 |
| Descriptor | 0x0000001D | 29 |
| BasicInformation | 0x00000028 | 40 |
| BridgedDeviceBasicInformation | 0x00000039 | 57 |
| ColorControl | 0x00000300 | 768 |

### OnOff

| Attribute | Hex | Dec |
| --- | --- | ---|
| onOff | 0x00000000 | 0 |

### LevelControl

| Attribute | Hex | Dec |
| --- | --- | ---|
| currentLevel | 0x00000000 | 0 |
| minLevel | 0x00000002 | 2 |
| maxLevel | 0x00000003 | 3 |

### BridgedDeviceBasicInformation

| Attribute | Hex | Dec |
| --- | --- | ---|
| nodeLabel | 0x00000005 | 5 |

### ColorControl

| Attribute | Hex | Dec |
| --- | --- | ---|
| currentHue | 0x00000000 | 0 |
| currentSaturation | 0x00000001 | 1 |
| colorTemperatureMireds | 0x00000007 | 7 |
| colorMode | 0x00000008 | 8 |
| colorTempPhysicalMinMireds | 0x0000400B | 16395 |
| colorTempPhysicalMinMireds | 0x0000400C | 16396 |
