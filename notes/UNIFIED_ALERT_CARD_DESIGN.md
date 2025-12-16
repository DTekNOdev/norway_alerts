# Unified Alert Card Design & Implementation Strategy

**Date:** December 16, 2025  
**Status:** Design Phase - Not Yet Implemented  
**Related:** UNIFIED_ALERT_SCHEMA.md  
**Goal:** Create a single Lovelace card that displays alerts from multiple sources/integrations

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Alert Standards Landscape](#alert-standards-landscape)
3. [Field Mapping Challenge](#field-mapping-challenge)
4. [Proposed Solution Architecture](#proposed-solution-architecture)
5. [Implementation Phases](#implementation-phases)
6. [Configuration Examples](#configuration-examples)
7. [Built-in Integration Profiles](#built-in-integration-profiles)
8. [CAP Standard Support](#cap-standard-support)
9. [Community Ecosystem](#community-ecosystem)

---

## Problem Statement

### Current Situation
- **met_alerts**: Weather alerts from MET Norway (wind, rain, snow, etc.)
- **varsom**: Geohazard alerts from NVE (landslides, floods, avalanches)
- Both use different field names and structures
- Users need separate cards/templates for each integration

### Desired Outcome
Create a **single, reusable Lovelace card** that can:
- Display alerts from met_alerts, varsom, and other sources
- Auto-detect integration types and map fields intelligently
- Support standard formats (CAP, IPAWS, etc.)
- Allow custom mapping for unknown integrations
- Provide consistent visual styling and UX
- Enable users to combine multiple alert sources in one view

### Key Design Principles
1. **Zero configuration for known integrations** (met_alerts, varsom)
2. **Convention over configuration** (smart defaults, auto-detection)
3. **Extensible for unknown integrations** (custom mapping support)
4. **Community-driven profiles** (share integration configs)
5. **Standards-based** (CAP support where applicable)

---

## Alert Standards Landscape

### CAP (Common Alerting Protocol) - Primary Standard

**CAP v1.2** is the OASIS international standard for emergency alerts.

**Used by:**
- FEMA (USA)
- NOAA Weather Service (USA)
- Met.no (Norway - partially)
- EU-Alert (European Union)
- Many government emergency services worldwide

**XML Structure:**
```xml
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>43b080713727</identifier>
  <sender>hsas@dhs.gov</sender>
  <sent>2003-04-02T14:39:01-05:00</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  
  <info>
    <category>Security</category>
    <event>Homeland Security Advisory System Update</event>
    <urgency>Immediate</urgency>
    <severity>Severe</severity>
    <certainty>Likely</certainty>
    <effective>2003-04-02T14:39:01-05:00</effective>
    <expires>2003-04-02T15:39:01-05:00</expires>
    <senderName>U.S. Government, Department of Homeland Security</senderName>
    <headline>Homeland Security Sets Code ORANGE</headline>
    <description>DHS has elevated the Homeland Security Advisory System...</description>
    <instruction>A threat of terrorist attacks...</instruction>
    
    <area>
      <areaDesc>U.S. nationwide</areaDesc>
    </area>
  </info>
</alert>
```

**CAP Severity Levels (Standard):**
- **Extreme**: Extraordinary threat to life or property
- **Severe**: Significant threat to life or property
- **Moderate**: Possible threat to life or property
- **Minor**: Minimal to no known threat to life or property
- **Unknown**: Severity unknown

**CAP Certainty Levels:**
- **Observed**: Determined to have occurred or to be ongoing
- **Likely**: Likely (p > ~50%)
- **Possible**: Possible but not likely (p <= ~50%)
- **Unlikely**: Not expected to occur (p ~ 0)
- **Unknown**: Certainty unknown

**CAP Urgency Levels:**
- **Immediate**: Responsive action SHOULD be taken immediately
- **Expected**: Responsive action SHOULD be taken soon (within next hour)
- **Future**: Responsive action SHOULD be taken in the near future
- **Past**: Responsive action is no longer required
- **Unknown**: Urgency not known

### Other Standards & Formats

#### IPAWS (Integrated Public Alert and Warning System - USA)
- CAP v1.2 based with US-specific extensions
- Used by FEMA, NOAA, local emergency management
- Wireless Emergency Alerts (WEA)
- Emergency Alert System (EAS)

#### EU-Alert
- CAP v1.2 with European profiles
- Pan-European mobile alert system
- Country-specific implementations

#### WMO CAP Profile
- World Meteorological Organization
- Meteorological and hydrological warnings
- Extensions for weather-specific events

#### Proprietary Formats
- **GeoJSON**: Met.no uses GeoJSON with custom properties (not pure CAP)
- **JSON APIs**: NVE Varsom, various weather services
- **RSS/Atom**: Legacy alert feeds
- **Custom XML**: National weather services

### Reality Check

**Most services don't follow standards exactly:**
- Met.no uses GeoJSON beta format (not XML CAP)
- NVE/Varsom uses proprietary JSON structure
- Many weather services have custom APIs
- Different countries use different implementations
- Legacy systems with old schemas
- **Estimate: Only 20-30% of alert sources use pure CAP format**

**Implication:** Card must be flexible and support field mapping, not just CAP standard.

---

## Field Mapping Challenge

### Example: Same Concept, Different Names

| Concept | met_alerts | varsom | CAP Standard | NWS (USA) | DWD (Germany) |
|---------|-----------|--------|--------------|-----------|---------------|
| **Title** | `title` | `main_text` | `info.headline` | `event` | `headline` |
| **Description** | `description` | `warning_text` | `info.description` | `description` | `description` |
| **Start Time** | `starttime` | `valid_from` | `info.effective` | `onset` | `start` |
| **End Time** | `endtime` | `valid_to` | `info.expires` | `expires` | `end` |
| **Severity** | `awareness_level_numeric` | `level` | `info.severity` | `severity` | `level` |
| **Location** | `area` | `municipalities` | `info.area.areaDesc` | `areaDesc` | `regionName` |
| **Instructions** | `instruction` | `advice_text` | `info.instruction` | `instruction` | `instruction` |

### The Problem

Creating a card that works with all these formats requires:
1. **Field name translation** (description vs warning_text vs info.description)
2. **Nested path handling** (CAP uses nested `info.xxx` structure)
3. **Value transformation** (severity text to numeric levels)
4. **Array handling** (single area string vs array of municipalities)
5. **Fallback logic** (try multiple field names)

---

## Proposed Solution Architecture

### Core Strategy: Intelligent Field Mapper

**Three-tier mapping approach:**

```
1. User Config (highest priority)
   ↓ (if not found)
2. Built-in Profile (for known integrations)
   ↓ (if not found)
3. Auto-detection with Common Aliases
   ↓ (if not found)
4. Fallback to null/empty
```

### 1. Field Mapper Class

```javascript
class AlertFieldMapper {
  constructor(config) {
    this.userMappings = config.field_mappings || {};
    this.profile = config.profile || null;
  }
  
  /**
   * Get a field value with intelligent fallback
   * @param {Object} alert - The alert object
   * @param {String} fieldName - Unified field name (e.g., 'title')
   * @returns {*} Field value or null
   */
  getField(alert, fieldName) {
    // 1. Check user-defined mapping first
    if (this.userMappings[fieldName]) {
      return this.getValue(alert, this.userMappings[fieldName]);
    }
    
    // 2. Check loaded profile mapping
    if (this.profile?.field_mappings?.[fieldName]) {
      return this.getValue(alert, this.profile.field_mappings[fieldName]);
    }
    
    // 3. Try unified schema field (direct match)
    if (alert[fieldName] !== undefined) {
      return alert[fieldName];
    }
    
    // 4. Try common aliases/patterns
    const aliases = this.getCommonAliases(fieldName);
    for (const alias of aliases) {
      // Try flat field
      if (alert[alias] !== undefined) {
        return alert[alias];
      }
      
      // Try nested path (e.g., "info.headline")
      const nested = this.getNestedValue(alert, alias);
      if (nested !== undefined) {
        return nested;
      }
    }
    
    return null;
  }
  
  /**
   * Common field name patterns for fallback
   */
  getCommonAliases(fieldName) {
    const aliasMap = {
      'title': [
        'title', 'headline', 'summary', 'name', 'event', 
        'main_text', 'MainText', 'info.headline'
      ],
      'description': [
        'description', 'desc', 'details', 'warning_text', 
        'WarningText', 'text', 'info.description'
      ],
      'severity_level': [
        'severity_level', 'level', 'urgency', 'priority', 
        'activity_level', 'ActivityLevel', 'info.severity'
      ],
      'severity_color': [
        'severity_color', 'color', 'level_name', 'severity'
      ],
      'valid_from': [
        'valid_from', 'starttime', 'start', 'effective', 'onset', 
        'ValidFrom', 'info.effective'
      ],
      'valid_to': [
        'valid_to', 'endtime', 'end', 'expires', 'ValidTo', 
        'info.expires'
      ],
      'area': [
        'area', 'areaDesc', 'region', 'location', 'county', 
        'municipality', 'info.area.areaDesc'
      ],
      'instruction': [
        'instruction', 'advice', 'advice_text', 'AdviceText', 
        'what_to_do', 'info.instruction'
      ],
      'consequences': [
        'consequences', 'consequence_text', 'ConsequenceText', 
        'impact', 'info.consequences'
      ],
      'certainty': [
        'certainty', 'confidence', 'probability', 'info.certainty'
      ],
      'alert_type': [
        'alert_type', 'event', 'type', 'category', 'danger_type', 
        'DangerTypeName', 'info.event'
      ],
      'url': [
        'url', 'link', 'web', 'info_url', 'details_url'
      ],
    };
    return aliasMap[fieldName] || [fieldName];
  }
  
  /**
   * Handle nested object paths like "info.area.areaDesc"
   */
  getNestedValue(obj, path) {
    return path.split('.').reduce((curr, prop) => curr?.[prop], obj);
  }
  
  /**
   * Get value from mapping config (string path or function)
   */
  getValue(obj, mapping) {
    if (typeof mapping === 'string') {
      return this.getNestedValue(obj, mapping);
    }
    if (typeof mapping === 'function') {
      return mapping(obj);
    }
    if (typeof mapping === 'object' && mapping.field) {
      const value = this.getNestedValue(obj, mapping.field);
      
      // Apply transformation
      if (mapping.map && value !== undefined) {
        return mapping.map[value];
      }
      if (mapping.transform) {
        // Could use template evaluation here
        return this.evaluateTransform(mapping.transform, value);
      }
      
      return value;
    }
    return null;
  }
}
```

### 2. Auto-Detection System

```javascript
class IntegrationDetector {
  static detect(entityId, alert) {
    // 1. Check if using unified schema v1
    if (alert.source && alert.alert_category) {
      return {
        type: 'unified_v1',
        source: alert.source,
        confidence: 'high'
      };
    }
    
    // 2. Check entity ID patterns
    const patterns = [
      { regex: /met_alerts/i, profile: 'met_alerts' },
      { regex: /varsom/i, profile: 'varsom' },
      { regex: /nws_alerts/i, profile: 'nws_alerts' },
      { regex: /dwd_/i, profile: 'dwd_warnwetter' },
    ];
    
    for (const pattern of patterns) {
      if (pattern.regex.test(entityId)) {
        return {
          type: 'profile',
          profile: pattern.profile,
          confidence: 'medium'
        };
      }
    }
    
    // 3. Check structure (CAP format detection)
    if (alert.info?.category && alert.info?.severity) {
      return {
        type: 'cap_standard',
        confidence: 'high'
      };
    }
    
    // 4. Check for specific field combinations
    if (alert.level && alert.main_text && alert.ValidFrom) {
      return {
        type: 'varsom_legacy',
        confidence: 'medium'
      };
    }
    
    if (alert.awareness_level && alert.eventAwarenessName) {
      return {
        type: 'met_alerts_legacy',
        confidence: 'medium'
      };
    }
    
    // 5. Fallback
    return {
      type: 'unknown',
      confidence: 'low'
    };
  }
}
```

### 3. Built-in Profile System

```javascript
const INTEGRATION_PROFILES = {
  'met_alerts': {
    name: 'MET Norway Weather Alerts',
    schema_version: 'unified_v1',
    // No field mappings needed - uses unified schema
  },
  
  'varsom': {
    name: 'Varsom Geohazard Alerts (NVE)',
    schema_version: 'unified_v1',
    // After Phase 2 implementation
  },
  
  'cap_standard': {
    name: 'CAP v1.2 Standard Format',
    description: 'Common Alerting Protocol - International Standard',
    field_mappings: {
      title: 'info.headline',
      description: 'info.description',
      instruction: 'info.instruction',
      severity_level: {
        field: 'info.severity',
        map: {
          'Extreme': 4,
          'Severe': 3,
          'Moderate': 2,
          'Minor': 1,
          'Unknown': 1
        }
      },
      severity_color: {
        field: 'info.severity',
        map: {
          'Extreme': 'red',
          'Severe': 'orange',
          'Moderate': 'yellow',
          'Minor': 'yellow',
          'Unknown': 'gray'
        }
      },
      certainty: 'info.certainty',
      valid_from: 'info.effective',
      valid_to: 'info.expires',
      area: 'info.area.areaDesc',
      alert_type: 'info.event',
      alert_category: 'info.category',
    }
  },
  
  'ipaws': {
    name: 'IPAWS (US Emergency Alerts)',
    description: 'Integrated Public Alert and Warning System (USA)',
    extends: 'cap_standard',
    // Inherits all CAP mappings
  },
  
  'nws_alerts': {
    name: 'US National Weather Service',
    description: 'NOAA/NWS weather alerts',
    field_mappings: {
      title: 'event',
      description: 'description',
      instruction: 'instruction',
      severity_level: {
        field: 'severity',
        map: {
          'Extreme': 4,
          'Severe': 3,
          'Moderate': 2,
          'Minor': 1,
          'Unknown': 1
        }
      },
      severity_color: {
        field: 'severity',
        map: {
          'Extreme': 'red',
          'Severe': 'orange',
          'Moderate': 'yellow',
          'Minor': 'yellow'
        }
      },
      certainty: 'certainty',
      valid_from: 'onset',
      valid_to: 'expires',
      area: 'areaDesc',
      alert_type: 'event',
      alert_category: 'category',
    }
  },
  
  'dwd_warnwetter': {
    name: 'DWD WarnWetter (Germany)',
    description: 'Deutscher Wetterdienst weather warnings',
    field_mappings: {
      title: 'headline',
      description: 'description',
      instruction: 'instruction',
      severity_level: 'level',
      valid_from: 'start',
      valid_to: 'end',
      area: 'regionName',
      alert_type: 'event',
    }
  },
};
```

---

## Implementation Phases

### Phase 1: Core Card (Q1 2026)

**Goal:** Basic card with met_alerts and varsom support

**Deliverables:**
- [ ] Card component structure
- [ ] Field mapper implementation
- [ ] Auto-detection for unified schema v1
- [ ] Built-in profiles for met_alerts and varsom
- [ ] Basic rendering (title, description, severity badge)
- [ ] HACS repository setup

**Timeline:** 2-3 weeks development

### Phase 2: Profile Library (Q1-Q2 2026)

**Goal:** Support major alert integrations

**Deliverables:**
- [ ] CAP standard profile
- [ ] IPAWS profile (USA)
- [ ] NWS alerts profile (USA)
- [ ] DWD WarnWetter profile (Germany)
- [ ] Profile documentation
- [ ] Profile contribution guidelines
- [ ] Community profile submission process

**Timeline:** 1-2 months (ongoing)

### Phase 3: Advanced Features (Q2 2026)

**Goal:** Enhanced UX and functionality

**Deliverables:**
- [ ] Map integration (show alert polygons)
- [ ] Severity filtering
- [ ] Alert grouping/sorting
- [ ] Animation/transitions
- [ ] Icon support
- [ ] Compact/detailed view modes
- [ ] Timeline view

**Timeline:** 2-3 months

### Phase 4: Community Ecosystem (Q2 2026+)

**Goal:** Self-sustaining community

**Deliverables:**
- [ ] Profile registry/marketplace
- [ ] Visual mapping tool (optional)
- [ ] Auto-update profiles from repo
- [ ] Profile rating/voting
- [ ] Integration with HA Community Store

**Timeline:** Ongoing

---

## Configuration Examples

### Zero Configuration (Recommended for Known Integrations)

```yaml
type: custom:unified-alert-card
entities:
  - sensor.met_alerts
  - sensor.varsom_alerts
```

**Result:** Auto-detects both integrations, uses unified schema, displays all alerts.

### With Display Options

```yaml
type: custom:unified-alert-card
entities:
  - sensor.met_alerts
  - sensor.varsom_alerts
show_map: true
severity_filter: 2  # Only show orange and red alerts
sort_by: severity  # or 'time', 'area'
view_mode: compact  # or 'detailed'
```

### With Custom Integration (Simple Mapping)

```yaml
type: custom:unified-alert-card
entities:
  - sensor.met_alerts
  - sensor.custom_weather_alerts
field_mappings:
  custom_weather_alerts:
    title: "alert_headline"
    description: "warning_message"
    severity_level: "priority"
    valid_from: "start_time"
    valid_to: "end_time"
```

### With Transformation (Advanced)

```yaml
type: custom:unified-alert-card
entities:
  - sensor.legacy_alert_system
field_mappings:
  legacy_alert_system:
    title: "properties.headline"
    severity_level: 
      field: "priority"
      transform: "{{ 4 - value }}"  # Invert priority scale
    severity_color:
      field: "level"
      map:
        5: "red"
        4: "orange"
        3: "yellow"
        2: "yellow"
        1: "green"
    valid_from: "effective_time"
```

### CAP Standard Alerts

```yaml
type: custom:unified-alert-card
entities:
  - sensor.cap_alerts  # Using CAP standard format
profile: cap_standard  # Explicitly use CAP profile
```

### Multiple Sources Combined

```yaml
type: custom:unified-alert-card
title: "All Active Alerts"
entities:
  - sensor.met_alerts          # Weather
  - sensor.varsom_alerts       # Geohazards
  - sensor.nws_alerts          # US Weather (if applicable)
  - sensor.custom_alerts       # Custom integration
severity_filter: 2             # Only orange/red
show_source_badge: true        # Show which integration
group_by: severity            # Group by severity level
```

---

## Built-in Integration Profiles

### Profile: met_alerts

```json
{
  "id": "met_alerts",
  "name": "MET Norway Weather Alerts",
  "version": "1.0",
  "schema": "unified_v1",
  "auto_detect": ["sensor.met_alerts", "met_alerts"],
  "description": "Weather alerts from MET Norway (wind, rain, snow, etc.)",
  "supported_features": [
    "severity_levels",
    "time_range",
    "geographic_area",
    "instructions",
    "consequences",
    "map_links"
  ]
}
```

### Profile: varsom

```json
{
  "id": "varsom",
  "name": "Varsom Geohazard Alerts",
  "version": "1.0",
  "schema": "unified_v1",
  "auto_detect": ["sensor.varsom", "varsom"],
  "description": "Landslide and flood alerts from NVE (Norway)",
  "supported_features": [
    "severity_levels",
    "time_range",
    "municipality_list",
    "danger_progression",
    "advice_text",
    "map_links"
  ]
}
```

### Profile: cap_standard

```json
{
  "id": "cap_standard",
  "name": "CAP v1.2 Standard",
  "version": "1.2",
  "schema": "cap",
  "auto_detect": ["info.category", "info.severity"],
  "description": "Common Alerting Protocol (OASIS Standard)",
  "field_mappings": {
    "title": "info.headline",
    "description": "info.description",
    "instruction": "info.instruction",
    "severity_level": {
      "field": "info.severity",
      "map": {
        "Extreme": 4,
        "Severe": 3,
        "Moderate": 2,
        "Minor": 1,
        "Unknown": 1
      }
    },
    "severity_color": {
      "field": "info.severity",
      "map": {
        "Extreme": "red",
        "Severe": "orange",
        "Moderate": "yellow",
        "Minor": "yellow",
        "Unknown": "gray"
      }
    },
    "valid_from": "info.effective",
    "valid_to": "info.expires",
    "certainty": "info.certainty",
    "area": "info.area.areaDesc",
    "alert_type": "info.event",
    "alert_category": "info.category"
  },
  "supported_features": [
    "severity_levels",
    "certainty_levels",
    "urgency_levels",
    "time_range",
    "geographic_area",
    "instructions"
  ]
}
```

---

## CAP Standard Support

### Why Support CAP?

1. **International Standard** - Used by many government agencies
2. **Well-Documented** - OASIS standard with clear specifications
3. **Wide Adoption** - FEMA, NOAA, EU-Alert, and more
4. **Future-Proof** - Likely to be adopted by more services

### CAP Field Mapping Strategy

Since CAP uses nested XML/JSON structure (`info.xxx`), the field mapper handles:

```javascript
// CAP alert structure
{
  "identifier": "...",
  "sender": "...",
  "sent": "...",
  "info": {
    "headline": "Severe Thunderstorm Warning",
    "description": "...",
    "severity": "Severe",
    "certainty": "Likely",
    "effective": "2025-12-16T12:00:00Z",
    "expires": "2025-12-16T18:00:00Z",
    "area": {
      "areaDesc": "Northern Counties"
    }
  }
}

// Mapped to unified schema
{
  "title": "Severe Thunderstorm Warning",  // from info.headline
  "description": "...",                    // from info.description
  "severity_level": 3,                     // from info.severity → mapped
  "severity_color": "orange",              // from info.severity → mapped
  "valid_from": "2025-12-16T12:00:00Z",   // from info.effective
  "valid_to": "2025-12-16T18:00:00Z",     // from info.expires
  "area": "Northern Counties",             // from info.area.areaDesc
  "certainty": "Likely",                   // from info.certainty
  "source": "cap_standard",
  "alert_category": "weather"
}
```

### Finding CAP Examples

**Known CAP Implementations:**

1. **NOAA/NWS (USA)**
   - https://api.weather.gov/alerts/active
   - Returns CAP format
   - May have Home Assistant integration already

2. **IPAWS (USA)**
   - https://apps.fema.gov/ipaws/
   - CAP with US extensions

3. **EU-Alert**
   - Country-specific implementations
   - Germany: DWD (may use CAP internally)
   - France: Météo-France
   - Spain: AEMET

4. **Met.no Legacy**
   - https://api.met.no/weatherapi/metalerts/2.0/current.xml
   - XML CAP format (vs their new GeoJSON)

5. **Environment Canada**
   - CAP-based weather alerts

**Action Items for CAP Support:**
- [ ] Test with NOAA API
- [ ] Test with Met.no XML endpoint
- [ ] Check if any HA integrations use CAP format
- [ ] Document CAP profile with real examples

---

## Community Ecosystem

### Profile Contribution Process

**Community members can contribute profiles for new integrations:**

1. **Create profile JSON file**
   ```json
   {
     "id": "my_alert_integration",
     "name": "My Alert Integration",
     "version": "1.0",
     "author": "username",
     "field_mappings": { ... },
     "auto_detect": ["sensor.my_alerts"],
     "tested_with": "v2024.12.0"
   }
   ```

2. **Submit to community repo**
   ```bash
   # Fork unified-alert-card repo
   git checkout -b add-my-integration-profile
   
   # Add profile
   cp my_integration.json profiles/community/
   
   # Submit PR
   git commit -m "Add profile for My Alert Integration"
   git push
   gh pr create --title "Add My Alert Integration profile"
   ```

3. **Profile review process**
   - Validation (correct JSON structure)
   - Testing (does it work?)
   - Documentation (clear description)
   - Approval by maintainers

4. **Profile published**
   - Included in next release
   - Available via auto-update
   - Listed in profile registry

### Profile Registry

**Potential future feature - searchable profile database:**

```
https://unified-alert-card.example.com/profiles

Search: [weather alerts germany    ] [Search]

Results:
┌─────────────────────────────────────────────┐
│ DWD WarnWetter (Germany)                    │
│ ⭐⭐⭐⭐⭐ 145 users | v1.2 | Built-in        │
│ Deutscher Wetterdienst weather warnings     │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ NINA Alerts (Germany)                       │
│ ⭐⭐⭐⭐☆ 34 users | v1.0 | Community        │
│ Federal warning app alerts                  │
│ [Install Profile]                           │
└─────────────────────────────────────────────┘
```

---

## Development Roadmap Summary

### Immediate Actions (Week 1-2)
1. Set up HACS repository structure
2. Implement field mapper class
3. Create basic card component
4. Add met_alerts and varsom profiles
5. Write developer documentation

### Short Term (Month 1-2)
1. Add CAP standard support
2. Test with NOAA/NWS if possible
3. Create configuration documentation
4. Release v1.0 (beta)
5. Gather user feedback

### Medium Term (Month 3-6)
1. Add more integration profiles
2. Implement map view
3. Add advanced filtering
4. Create visual styling options
5. Release v1.0 (stable)

### Long Term (6+ months)
1. Community profile submissions
2. Profile registry (optional)
3. Visual mapping tool (optional)
4. Additional features based on feedback
5. Ongoing maintenance

---

## Technical Architecture

### File Structure

```
unified-alert-card/
├── README.md
├── hacs.json
├── package.json
├── rollup.config.js
├── src/
│   ├── unified-alert-card.js       # Main card component
│   ├── field-mapper.js             # Field mapping logic
│   ├── integration-detector.js     # Auto-detection
│   ├── renderers/
│   │   ├── compact-renderer.js
│   │   ├── detailed-renderer.js
│   │   └── timeline-renderer.js
│   ├── styles/
│   │   └── card-styles.js
│   └── utils/
│       ├── date-utils.js
│       └── severity-utils.js
├── profiles/
│   ├── built-in/
│   │   ├── met_alerts.json
│   │   ├── varsom.json
│   │   ├── cap_standard.json
│   │   ├── ipaws.json
│   │   └── nws_alerts.json
│   ├── community/
│   │   └── README.md
│   └── schema.json                 # Profile JSON schema
├── docs/
│   ├── configuration.md
│   ├── profile-creation.md
│   └── examples.md
└── test/
    ├── field-mapper.test.js
    └── integration-detector.test.js
```

### Card Component Structure

```javascript
class UnifiedAlertCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this.fieldMapper = new AlertFieldMapper(config);
    this.detector = new IntegrationDetector();
  }
  
  set hass(hass) {
    this._hass = hass;
    this.render();
  }
  
  render() {
    const alerts = this.collectAlerts();
    const filtered = this.filterAlerts(alerts);
    const sorted = this.sortAlerts(filtered);
    
    this.innerHTML = this.renderAlerts(sorted);
  }
  
  collectAlerts() {
    const alerts = [];
    for (const entityId of this.config.entities) {
      const entity = this._hass.states[entityId];
      const entityAlerts = entity.attributes.alerts || [];
      
      for (const alert of entityAlerts) {
        // Detect integration type
        const detection = this.detector.detect(entityId, alert);
        
        // Normalize alert using field mapper
        const normalized = this.normalizeAlert(alert, detection);
        
        alerts.push({
          ...normalized,
          _original: alert,
          _entity_id: entityId,
          _detection: detection
        });
      }
    }
    return alerts;
  }
  
  normalizeAlert(alert, detection) {
    // Load profile if detected
    if (detection.type === 'profile') {
      this.fieldMapper.profile = INTEGRATION_PROFILES[detection.profile];
    }
    
    // Map all unified fields
    return {
      title: this.fieldMapper.getField(alert, 'title'),
      description: this.fieldMapper.getField(alert, 'description'),
      severity_level: this.fieldMapper.getField(alert, 'severity_level'),
      severity_color: this.fieldMapper.getField(alert, 'severity_color'),
      valid_from: this.fieldMapper.getField(alert, 'valid_from'),
      valid_to: this.fieldMapper.getField(alert, 'valid_to'),
      area: this.fieldMapper.getField(alert, 'area'),
      instruction: this.fieldMapper.getField(alert, 'instruction'),
      // ... etc
    };
  }
}
```

---

## Next Steps & Action Items

### Before Implementation
- [ ] Review and approve this design document
- [ ] Decide on project timeline
- [ ] Choose initial supported integrations beyond met_alerts/varsom
- [ ] Research existing HA alert integrations

### Implementation Prep
- [ ] Set up HACS repository
- [ ] Choose build tools (Rollup, Webpack, etc.)
- [ ] Set up TypeScript (optional but recommended)
- [ ] Create project structure

### First Milestone
- [ ] Implement field mapper
- [ ] Create basic card rendering
- [ ] Add met_alerts profile
- [ ] Add varsom profile
- [ ] Test with both integrations
- [ ] Write basic documentation

### Future Considerations
- Visual mapping tool worth it?
- Profile registry needed?
- Should we support non-alert entities?
- Localization/translation support?
- Mobile app compatibility?

---

## References & Resources

- **CAP Specification:** http://docs.oasis-open.org/emergency/cap/v1.2/
- **IPAWS:** https://www.fema.gov/emergency-managers/practitioners/integrated-public-alert-warning-system
- **NOAA Alerts API:** https://www.weather.gov/documentation/services-web-api
- **Met.no API:** https://api.met.no/weatherapi/metalerts/2.0/documentation
- **NVE Varsom API:** https://api.nve.no/doc/
- **Home Assistant Lovelace Card Development:** https://developers.home-assistant.io/docs/frontend/custom-ui/lovelace-custom-card/

---

## Appendix: Real-World Integration Examples

### Integration: met_alerts (Norway)
- **Type:** Weather
- **Format:** GeoJSON with custom properties
- **Fields:** awareness_level, event, description, area
- **Status:** Unified schema v1 ✅

### Integration: varsom (Norway)
- **Type:** Geohazard
- **Format:** Custom JSON
- **Fields:** level, main_text, municipalities, ValidFrom/ValidTo
- **Status:** Unified schema v1 pending

### Integration: NWS Alerts (USA)
- **Type:** Weather
- **Format:** GeoJSON with CAP-like properties
- **Fields:** event, severity, description, onset, expires
- **Status:** Profile needed

### Integration: DWD (Germany)
- **Type:** Weather
- **Format:** Custom JSON/XML
- **Fields:** headline, description, level, start, end
- **Status:** Profile needed

### Integration: MeteoAlarm (Europe)
- **Type:** Weather
- **Format:** RSS/CAP
- **Fields:** CAP standard fields
- **Status:** CAP profile should work

---

**END OF DOCUMENT**

**Status:** Ready for discussion and implementation when time permits  
**Next Review:** When ready to implement unified alert card  
**Contact:** See project maintainers
