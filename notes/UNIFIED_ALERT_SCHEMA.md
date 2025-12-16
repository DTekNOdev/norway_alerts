# Unified Alert Schema for Cross-Integration Compatibility

**Date:** December 16, 2025
**Status:** Phase 1 Implemented (met_alerts), Phase 2 Pending (varsom)
**Goal:** Enable a single Lovelace card to display alerts from both met_alerts and varsom integrations

---

## Background

Currently, we have two alert integrations with different attribute structures:
- **met_alerts**: Weather alerts from MET Norway (wind, rain, snow, etc.)
- **varsom**: Geohazard alerts from NVE (landslides, floods, avalanches)

Both provide alerts through an `alerts` attribute array, but the field names and structures differ significantly, making it difficult to create a unified dashboard card or template.

## Goal

Create a **common attribute mapping** that both integrations support, enabling:
1. A single Lovelace custom card that works with both integrations
2. Reusable Jinja2 templates that work for both alert types
3. Future-proof schema for additional alert sources (e.g., maritime alerts, fire warnings)

---

## Unified Alert Schema v1.0

### Core Fields (All Integrations MUST Provide)

```json
{
  // ===== IDENTIFIERS =====
  "id": "string",                       // Unique alert ID
  "source": "met_alerts|varsom|...",    // Integration source identifier
  
  // ===== SEVERITY (UNIFIED) =====
  "severity_level": 1-4,                // 1=Yellow, 2=Orange, 3=Red, 4=Purple
  "severity_color": "yellow|orange|red|purple",
  "severity_name": "string",            // "Moderate", "Severe", "Extreme", etc.
  
  // ===== TIMING (UNIFIED) =====
  "valid_from": "ISO8601",              // Start time (e.g., "2025-12-16T00:00:00+00:00")
  "valid_to": "ISO8601",                // End time
  
  // ===== LOCATION (UNIFIED) =====
  "area": "string",                     // Primary area name (single string)
  "areas": ["string"],                  // All affected areas (array)
  
  // ===== CONTENT (UNIFIED) =====
  "title": "string",                    // Alert headline/summary
  "description": "string",              // Main description/warning text
  "instruction": "string",              // What to do / advice
  "consequences": "string",             // Potential impact/consequences
  
  // ===== METADATA =====
  "alert_type": "string",               // Type: "wind", "rain", "landslide", "flood", etc.
  "alert_category": "weather|geohazard", // High-level category
  "url": "string"                       // Link to detailed information
}
```

### Optional Fields (Integration-Specific)

```json
{
  // ===== WEATHER-SPECIFIC (met_alerts) =====
  "certainty": "Possible|Likely|Observed",
  "event_awareness_name": "string",     // e.g., "moderate-wind"
  "contact": "string",                  // Contact URL
  "resources": [                        // Array of resource links
    {"uri": "...", "mimeType": "..."}
  ],
  
  // ===== GEOHAZARD-SPECIFIC (varsom) =====
  "master_id": "string",                // NVE master ID
  "danger_type": "string",              // "Jordskred", "Flom", "Snøskred"
  "warning_type": "landslide|flood|avalanche",
  "danger_increases": "ISO8601",        // When danger increases
  "danger_decreases": "ISO8601",        // When danger decreases
  "municipalities": ["string"]          // Full municipality list
}
```

---

## Current Implementation Status

### ✅ Phase 1: met_alerts (IMPLEMENTED)

**Status:** Complete - unified fields added as aliases (December 16, 2025)

**Implementation:** Additive-only changes to maintain backward compatibility

```python
# met_alerts/custom_components/met_alerts/sensor.py
alerts.append({
    # ===== EXISTING FIELDS (backward compatibility) =====
    "title": title,
    "starttime": starttime,
    "endtime": endtime,
    "description": props.get("description", ""),
    "awareness_level": awareness_level,
    "awareness_level_numeric": awareness_level_numeric,
    "awareness_level_color": awareness_level_color,
    "certainty": props.get("certainty", ""),
    "severity": props.get("severity", ""),
    "instruction": props.get("instruction", ""),
    "contact": props.get("contact", ""),
    "resources": resources,
    "area": props.get("area", ""),
    "event_awareness_name": props.get("eventAwarenessName", ""),
    "consequences": props.get("consequences", ""),
    
    # ===== UNIFIED SCHEMA FIELDS =====
    "source": "met_alerts",
    "alert_category": "weather",
    "alert_type": props.get("event", ""),
    "severity_level": int(awareness_level_numeric) if awareness_level_numeric else 1,
    "severity_color": awareness_level_color,
    "severity_name": props.get("severity", ""),
    "valid_from": starttime,
    "valid_to": endtime,
    "areas": [props.get("area", "")] if props.get("area") else [],
    "url": resource_url,
})
```

**Backward Compatibility:** ✅ All existing fields retained, no breaking changes

### ⏳ Phase 2: varsom (PENDING DISCUSSION)

**Status:** Planned - awaiting design discussion

**Current varsom Alert Structure:**
```json
{
  "id": "999999",
  "master_id": "...",
  "level": 3,
  "level_name": "red",
  "danger_type": "Jordskred",
  "warning_type": "landslide",
  "municipalities": ["Testville", "..."],
  "valid_from": "2025-12-16T00:00:00",
  "valid_to": "2025-12-17T23:59:59",
  "danger_increases": "...",
  "danger_decreases": "...",
  "main_text": "Test Alert...",
  "warning_text": "Det er moderat fare...",
  "advice_text": "Unngå opphold...",
  "consequence_text": "Jordskred kan...",
  "url": "https://www.varsom.no/..."
}
```

**Proposed Changes for varsom:**

#### Option A: Add Unified Aliases (Recommended - Backward Compatible)

```python
# varsom/custom_components/varsom/sensor.py
alert_dict = {
    # ===== EXISTING FIELDS (keep all) =====
    "id": forecast_id,
    "master_id": master_id,
    "level": int(activity_level),
    "level_name": ACTIVITY_LEVEL_NAMES.get(activity_level, "green"),
    "danger_type": alert.get("DangerTypeName", ""),
    "warning_type": alert.get("_warning_type", "unknown"),
    "municipalities": municipalities,
    "valid_from": alert.get("ValidFrom", ""),
    "valid_to": alert.get("ValidTo", ""),
    "danger_increases": alert.get("DangerIncreaseDateTime"),
    "danger_decreases": alert.get("DangerDecreaseDateTime"),
    "main_text": alert.get("MainText", ""),
    "warning_text": alert.get("WarningText", ""),
    "advice_text": alert.get("AdviceText", ""),
    "consequence_text": alert.get("ConsequenceText", ""),
    "url": varsom_url,
    
    # ===== UNIFIED SCHEMA ALIASES =====
    "source": "varsom",
    "alert_category": "geohazard",
    "alert_type": alert.get("DangerTypeName", "").lower(),
    "severity_level": int(activity_level),        # Already aligned!
    "severity_color": ACTIVITY_LEVEL_NAMES.get(activity_level, "green"),
    "severity_name": ACTIVITY_LEVEL_NAMES.get(activity_level, "green").title(),
    "title": alert.get("MainText", ""),           # Map main_text → title
    "description": alert.get("WarningText", ""),  # Map warning_text → description
    "instruction": alert.get("AdviceText", ""),   # Map advice_text → instruction
    "consequences": alert.get("ConsequenceText", ""),  # Already aligned!
    "area": municipalities[0] if municipalities else "",
    "areas": municipalities,
}
```

#### Option B: Rename Fields (Breaking Change - Not Recommended)

Replace old field names with unified names. **NOT RECOMMENDED** due to breaking changes for existing users.

---

## Field Mapping Reference

### met_alerts → Unified Schema

| Original Field | Unified Field | Notes |
|---|---|---|
| `awareness_level_numeric` | `severity_level` | Already numeric 1-3 |
| `awareness_level_color` | `severity_color` | Already yellow/orange/red |
| `starttime` | `valid_from` | Alias added |
| `endtime` | `valid_to` | Alias added |
| `area` | `area` | Direct mapping |
| `area` | `areas` | Wrapped in array |
| `event` | `alert_type` | e.g., "gale", "rain" |
| `resources[0].uri` | `url` | First resource URL |
| N/A | `source` | Set to "met_alerts" |
| N/A | `alert_category` | Set to "weather" |

**Compatibility:** ✅ 100% backward compatible - all original fields retained

### varsom → Unified Schema (Proposed)

| Original Field | Unified Field | Notes |
|---|---|---|
| `level` | `severity_level` | Already numeric 1-4 ✅ |
| `level_name` | `severity_color` | Already yellow/orange/red ✅ |
| `valid_from` | `valid_from` | Already aligned ✅ |
| `valid_to` | `valid_to` | Already aligned ✅ |
| `municipalities[0]` | `area` | First municipality |
| `municipalities` | `areas` | Already aligned ✅ |
| `main_text` | `title` | NEW alias |
| `warning_text` | `description` | NEW alias |
| `advice_text` | `instruction` | NEW alias |
| `consequence_text` | `consequences` | Already aligned ✅ |
| `danger_type` | `alert_type` | NEW alias (lowercase) |
| N/A | `source` | Set to "varsom" |
| N/A | `alert_category` | Set to "geohazard" |

**Compatibility:** ✅ If Option A used - 100% backward compatible

---

## Usage Examples

### Unified Lovelace Card (Future)

```javascript
// Single card configuration works for both integrations
class UnifiedAlertCard extends HTMLElement {
  render(alert) {
    return `
      <ha-card header="${alert.source.toUpperCase()} Alert">
        <div class="card-content">
          <h3 style="color: ${alert.severity_color}">${alert.title}</h3>
          <p><b>Severity:</b> ${alert.severity_name} (${alert.severity_color})</p>
          <p><b>Valid:</b> ${alert.valid_from} to ${alert.valid_to}</p>
          <p><b>Area:</b> ${alert.area}</p>
          <p>${alert.description}</p>
          ${alert.instruction ? `<p><b>Action:</b> ${alert.instruction}</p>` : ''}
          <a href="${alert.url}">More info</a>
        </div>
      </ha-card>
    `;
  }
}
```

### Unified Jinja2 Template

```jinja2
{# Works for both met_alerts and varsom! #}
{% set met_alerts = state_attr('sensor.met_alerts', 'alerts') or [] %}
{% set varsom_alerts = state_attr('sensor.varsom_alerts', 'alerts') or [] %}
{% set all_alerts = met_alerts + varsom_alerts %}

{% for alert in all_alerts | sort(attribute='severity_level', reverse=True) %}
<div style="border-left: 4px solid {{ alert.severity_color }}; padding: 10px; margin: 5px 0;">
  <h3>{{ alert.title }}</h3>
  <p><b>Source:</b> {{ alert.source | upper }} ({{ alert.alert_category }})</p>
  <p><b>Type:</b> {{ alert.alert_type }}</p>
  <p><b>Severity:</b> {{ alert.severity_color | upper }} - {{ alert.severity_name }}</p>
  <p><b>Valid:</b> {{ alert.valid_from }} to {{ alert.valid_to }}</p>
  <p><b>Area:</b> {{ alert.area }}</p>
  <p>{{ alert.description }}</p>
  {% if alert.instruction %}
  <p><i>{{ alert.instruction }}</i></p>
  {% endif %}
  <a href="{{ alert.url }}">Details</a>
</div>
{% endfor %}
```

### Filter by Severity Across Both Sources

```jinja2
{# Show only RED/EXTREME alerts from both integrations #}
{% set all_alerts = (state_attr('sensor.met_alerts', 'alerts') or []) + 
                    (state_attr('sensor.varsom_alerts', 'alerts') or []) %}
{% set critical = all_alerts | selectattr('severity_level', 'ge', 3) | list %}

{% if critical | count > 0 %}
🚨 CRITICAL ALERTS ({{ critical | count }})
{% for alert in critical %}
• [{{ alert.source | upper }}] {{ alert.title }} ({{ alert.area }})
{% endfor %}
{% endif %}
```

---

## Benefits

### For Users
- ✅ Single template/card works for all alert types
- ✅ Easier to create unified alert dashboards
- ✅ Consistent filtering and sorting across alert sources
- ✅ No breaking changes to existing dashboards

### For Developers
- ✅ Standard schema for future alert integrations
- ✅ Reduced complexity in Lovelace cards
- ✅ Clear migration path
- ✅ Easier testing and maintenance

### For the Ecosystem
- ✅ Encourages consistent alert handling across HA
- ✅ Makes custom cards reusable
- ✅ Facilitates alert aggregation and prioritization

---

## Migration Timeline

### ✅ Phase 1 (December 2025) - COMPLETE
- [x] Design unified schema
- [x] Implement in met_alerts (additive)
- [x] Document schema
- [x] Update met_alerts CARD_EXAMPLES.md

### ⏳ Phase 2 (January 2026) - PENDING
- [ ] Discussion: varsom field mapping strategy
- [ ] Implement in varsom (Option A recommended)
- [ ] Update varsom documentation
- [ ] Test backward compatibility

### 🔮 Phase 3 (Q1 2026) - FUTURE
- [ ] Build unified Lovelace alert card
- [ ] Publish card to HACS
- [ ] Update both integrations' documentation
- [ ] Create unified template library

### 🔮 Phase 4 (Q2 2026+) - FUTURE
- [ ] Add maritime alerts support (if desired)
- [ ] Consider additional alert sources
- [ ] Deprecate old field names (with warnings)

---

## Discussion Points for varsom Implementation

### Questions to Resolve:

1. **Field Naming Strategy:**
   - Option A: Add unified aliases (keep all existing fields) ← **RECOMMENDED**
   - Option B: Rename fields (breaking change)
   - Option C: Hybrid approach?

2. **Severity Level Alignment:**
   - varsom has 4 levels (1-4: Green/Yellow/Orange/Red)
   - met_alerts has 3 levels (1-3: Yellow/Orange/Red)
   - Should unified schema support 1-4 or normalize to 1-3?
   - Current proposal: Support 1-4 (more flexible)

3. **Area Representation:**
   - varsom has multiple municipalities
   - met_alerts has single area string
   - Current proposal: `area` = primary (string), `areas` = full list (array)
   - Should we concatenate for `area` or just use first?

4. **Language/Translation:**
   - varsom has Norwegian danger_type names
   - Should `alert_type` be translated or kept in source language?
   - Current proposal: Keep original, let card handle translation

5. **URL Format:**
   - Both have different URL structures
   - Current proposal: Direct mapping (keep as-is)
   - Alternative: Normalize URL structure?

6. **Time Precision:**
   - varsom has danger_increases/decreases
   - met_alerts doesn't have equivalent
   - Current proposal: Keep as optional fields

---

## Testing Checklist

### met_alerts Tests (Complete)
- [x] All original attributes still present
- [x] New unified attributes populated correctly
- [x] Backward compatibility with existing templates
- [x] Test mode generates unified fields
- [x] No breaking changes in entity state

### varsom Tests (Pending)
- [ ] All original attributes still present
- [ ] New unified attributes populated correctly
- [ ] Backward compatibility with existing dashboards
- [ ] Municipality filtering works with new fields
- [ ] Test mode generates unified fields
- [ ] No breaking changes in entity state

### Cross-Integration Tests (Future)
- [ ] Template using only unified fields works with both
- [ ] Severity sorting works correctly across sources
- [ ] Area filtering works as expected
- [ ] Time-based filtering works correctly
- [ ] Unified card displays both alert types correctly

---

## References

- **met_alerts repository:** `/met_alerts/`
- **varsom repository:** `/no.varsom/`
- **Met.no API:** https://api.met.no/weatherapi/metalerts/2.0/documentation
- **NVE Varsom API:** https://api.nve.no/doc/
- **CAP Standard:** http://docs.oasis-open.org/emergency/cap/v1.2/

---

## Change Log

| Date | Change | Author |
|---|---|---|
| 2025-12-16 | Initial schema design and documentation | AI/JC |
| 2025-12-16 | Phase 1 implementation in met_alerts | AI/JC |
| TBD | Phase 2 implementation in varsom | Pending |

---

## Approval Status

- ✅ **met_alerts:** Implemented and ready for PR
- ⏳ **varsom:** Pending discussion and approval
- ⏳ **Unified Card:** Pending Phase 2 completion

---

**END OF DOCUMENT**
