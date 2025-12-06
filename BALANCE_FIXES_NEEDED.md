# Critical Balance Issues - Week 1 Profitability

## Problem Summary

The simulation is far too easy - players are making $1,855 profit in Week 1 with ZERO brand recognition or customer loyalty.

## Issues Found

### 1. **History Not Rendering Despite Data Existing**

- **Backend**: `/history/comparison` returns valid data
- **Frontend**: HistoryViewer shows "No History Yet" even with data
- **Cause**: The condition check in HistoryViewer.tsx line 114 was checking `comparison && Object.keys...` but the data structure has participants
- **Status**: ALREADY FIXED in previous commit

### 2. **Unrealistic Week 1 Volume**

**Current State**:

- 490 wash loads + 490 dry loads = ~70 customers/day
- For ref: Average laundromat serves 20-30 customers/day
- With 0% brand recognition, should be ~5-10 customers/day initially

**Per Worldbook** (`1_2_starting_resources_equitment.md`):

```
Brand Recognition: 0% (unknown)
Customer Database: 0 registered customers
Social Score: 50/100 (Neutral - no loyalty)
```

**Per Simulation Time** (`3_0_simularion_time_system.md`):

```
Week 1-2: Setup & Launch
• Customer awareness building
• Initial branding and positioning
```

### 3. **Missing Startup Struggles**

According to worldbook, Week 1-2 should focus on:

- Building awareness (NOT high volume)
- Establishing vendor relationships
- Initial positioning

Current implementation skips straight to profitability.

---

## Root Causes

### Issue A: Customer Generation Too High

Location: `src/engine/game_engine.py` or customer sim logic

**Current**: Generates customers based only on:

1. Machine count (15 machines)
2. Price attractiveness
3. Social score

**Missing**:

1. **Brand Recognition** modifier (should be 0% → ~10% of normal traffic)
2. **Time-in-business** modifier (new vs established)
3. **Word-of-mouth** ramp-up (gradual growth)

### Issue B: No Inventory Depletion Costs

**Current State**:

- Started with 200 detergent (free inventory value ~$16-20)
- Used ~160 loads worth of detergent
- Only charged $40 COGS

**Should Be**:

- Initial inventory should count as COGS when used
- OR start with minimal inventory forcing immediate purchase
- Detergent cost per load: $0.10-0.15 → 160 loads = $16-24 deducted

### Issue C: Revenue Calculation Ignores Market Reality

All 3 laundromats show IDENTICAL numbers:

- Balance: $6,327
- Revenue: $2,973
- Net Income: $1,855

This suggests:

1. Customer distribute equally regardless of price/quality
2. No competitive dynamics
3. No differentiation impact

---

## Recommended Fixes (Priority Order)

### 🔴 CRITICAL - Fix Customer Volume Calculation

**File**: `src/engine/game_engine.py` (or wherever customer flow is calculated)

Add **Brand Recognition** system:

```python
class LaundromatState:
    def __init__(self):
        # ... existing
        self.brand_recognition = 0.0  # 0-100% scale
        self.weeks_in_business = 0
        self.loyal_customers = 0

def calculate_customer_arrivals(state: LaundromatState, base_demand: int) -> int:
    """Calculate realistic customer arrivals based on brand recognition"""

    # Brand recognition ramps up slowly
    recognition_multiplier = state.brand_recognition / 100.0

    # Week-based ramp (first 4 weeks are slow)
    if state.weeks_in_business <= 1:
        time_multiplier = 0.15  # Only 15% of normal traffic
    elif state.weeks_in_business <= 2:
        time_multiplier = 0.30  # 30% of normal
    elif state.weeks_in_business <= 4:
        time_multiplier = 0.50  # 50% of normal
    elif state.weeks_in_business <= 6:
        time_multiplier = 0.75  # 75% of normal
    else:
        time_multiplier = 1.0   # Full traffic

    # Social score affects retention, not initial traffic
    social_modifier = (state.social_score.total_score / 100.0) * 0.2 + 0.8

    # Price sensitivity (higher price = fewer customers initially)
    price_modifier = max(0.5, 1.0 - ((state.price - 3.0) / 10.0))

    final_arrivals = int(base_demand * time_multiplier * recognition_multiplier * social_modifier * price_modifier)

    return max(1, final_arrivals)  # At least 1 customer
```

**Expected Impact**: Week 1 customers drop from ~490 to ~70-100 total (10-14/day)

---

### 🟠 HIGH - Fix Initial Inventory Costs

**File**: `src/world/laundromat.py` or wherever inventory is tracked

Option A: **Count initial inventory as COGS**

```python
def process_week_revenue(self):
    # Track inventory usage
    detergent_used = self.loads_serviced
    detergent_cost = detergent_used * 0.12  # $0.12/load avg

    # Deduct from inventory
    self.inventory['detergent'] -= detergent_used

    # Add to COGS (even if "free" starting inventory)
    self.week_cogs += detergent_cost
```

Option B: **Start with minimal inventory**

```python
# In initial state setup
"inventory": {
    "detergent": 20,    # Only 20 loads (forces Week 1 purchase)
    "softener": 10,     # Minimal starter
    "dryer_sheets": 30,
    "cleaning_supplies": 2
}
```

**Expected Impact**: Week 1 profit drops by $150-200

---

### 🟡 MEDIUM - Add Brand Recognition Growth System

**File**: `src/engine/game_engine.py`

```python
def update_brand_recognition(state: LaundromatState):
    """Organic brand growth based on actions"""

    # Base growth from operations
    if state.social_score.total_score >= 70:
        state.brand_recognition += 2.0  # Good reputation spreads
    elif state.social_score.total_score >= 50:
        state.brand_recognition += 0.5  # Neutral = slow growth
    else:
        state.brand_recognition -= 0.5  # Bad rep hurts

    # Marketing boost
    if state.marketing_boost > 0:
        state.brand_recognition += (state.marketing_boost * 0.1)

    # Word of mouth (loyal customers promote)
    state.brand_recognition += (state.loyal_customers * 0.01)

    # Cap at 100%
    state.brand_recognition = min(100.0, max(0.0, state.brand_recognition))
```

---

### 🟢 LOW - Add Startup Phase Messaging

Show players they're in "awareness building" phase:

```python
if state.weeks_in_business <= 2:
    events.append({
        "type": "INFO",
        "message": "Week 1-2: Focus on building customer awareness. Word-of-mouth takes time!"
    })
```

---

## Target Metrics

### Week 1 (Current vs Target)

| Metric              | Current     | Target             | Reasoning                                         |
| ------------------- | ----------- | ------------------ | ------------------------------------------------- |
| **Customers/day**   | 70          | 10-15              | 0% brand recognition, unknown business            |
| **Weekly Revenue**  | $2,973      | $600-$900          | 10-15 customers × 6 days × $10 avg                |
| **Weekly Expenses** | $1,000      | $1,100             | Should include inventory depletion                |
| **Net Income**      | **+$1,855** | **-$200 to +$100** | Startup phase should be break-even or slight loss |
| **Ending Balance**  | $6,327      | $2,400-$2,600      | Close to starting $2,500                          |

### Week 4 (Target Progression)

| Metric            | Target        | Reasoning                                   |
| ----------------- | ------------- | ------------------------------------------- |
| Customers/day     | 25-30         | Word spreading, ~50% of mature volume       |
| Brand Recognition | 25-30%        | Organic growth + maybe 1 marketing campaign |
| Weekly Revenue    | $1,500-$2,000 | Growing customer base                       |
| Net Income        | $300-$500     | Starting to see profit                      |

---

## Implementation Priority

1. ✅ **Fix history rendering** (DONE)
2. 🔴 **Add brand_recognition field to LaundromatState**
3. 🔴 **Modify customer arrival calculation to use brand recognition + weeks_in_business**
4. 🟠 **Fix inventory cost accounting (initial inventory = COGS)**
5. 🟡 **Add brand recognition growth logic to weekly processing**
6. 🟢 **Add startup phase UI messaging**

---

## Testing Checklist

After fixes:

- [ ] Start new game → Week 1 revenue should be $600-$900
- [ ] Week 1 profit should be -$200 to +$100
- [ ] Detergent inventory should deplete and force purchase
- [ ] Brand recognition should start at 0% and grow slowly
- [ ] Week 4 should show clear growth progression
- [ ] Marketing campaigns should boost brand recognition
- [ ] High social score should accelerate brand growth

---

## Files To Modify

1. `src/world/laundromat.py` - Add brand_recognition field
2. `src/engine/game_engine.py` - Modify customer calculation
3. `src/engine/game_engine.py` - Add brand growth logic
4. `src/server.py` - Serialize brand_recognition in state
5. `frontend/src/types.ts` - Add brand_recognition to Laundromat type (optional, for UI display)
