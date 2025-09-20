# Bin Buddy for Home Assistant - Blacktown

Bin Buddy is a Home Assistant integration for tracking bin collection dates in the Blacktown area. This extension provides sensors for your bin schedules, helping you stay on top of waste, recycling, and garden bin collections.

## Features

- Sensors for food & garden waste, general waste, and recycling bin collection dates.
- No built-in polling—users control update frequency via Home Assistant automations.

## Installation

### Option 1: Install via HACS (Recommended)

1. In Home Assistant, go to **HACS** > **Integrations**.
2. Click the three dots menu and select **Custom repositories**.
3. Add this repository URL and select **Integration** as the category.
4. Search for "Bin Buddy - Blacktown" in HACS and install.
5. Restart Home Assistant.

### Option 2: Manual Installation

1. Copy the integration files to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

After installation, configure the integration via the UI or YAML.


## Usage

### Updating Bin Collection Dates

This integration does **not** poll for updates automatically. You must set up your own automation to refresh bin collection dates.

Example automation to update daily at midnight:

```yaml
alias: Update bins
description: ""
trigger:
    - platform: time
        at: "00:00:00"
condition: []
action:
    - service: homeassistant.update_entity
        target:
            entity_id:
                - date.bin_collection_food_and_garden_waste
                - date.bin_collection_general_waste
                - date.bin_collection_recycling
mode: single
```

### Use helpers to decide when to show an indicator
I've created template binary sensors that turn on when it is the day before and day of collection like so:
```python
{{ states("date.bin_collection_general_waste") == now().strftime('%Y-%m-%d') 
or states("date.bin_collection_general_waste") == (now()+timedelta(days=1)).date().strftime('%Y-%m-%d') }}
```

### Show an indicator on your dashboard
```yaml
type: entity
show_name: false
show_state: false
show_icon: true
entity: date.bin_collection_general_waste
icon: mdi:delete
color: red
show_entity_picture: false
visibility:
  - condition: state
    entity: binary_sensor.show_red_bin_icon
    state: "on"
```

## License

MIT License.