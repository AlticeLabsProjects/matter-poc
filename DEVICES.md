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

### BridgedDeviceBasicInformation

| Attribute | Hex | Dec |
| --- | --- | ---|
| nodeLabel | 0x00000005 | 5 |
