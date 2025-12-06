3

## 🌍 PART 2: THE WORLD BIBLE (Rules & Regulations)

The "World Bible" is the foundational rulebook governing the simulation. All participants—human and AI—must operate within these constraints.

# 2 Environment Overview
┌─────────────────────────────────────────────────────────────────────────┐
│                         NEIGHBORHOOD ENVIRONMENT                        │
|                               this includes                             | 
├─────────────────────────────────────────────────────────────────────────┤
│ • Mixed urban/suburban setting with diverse demographics                │
│ • Shared customer pool across all laundromats                           │
└─────────────────────────────────────────────────────────────────────────┘

### 2.1.3 Neighborhood Map & Zones


┌─────────────────────────────────────────────────────────────────────────┐
│                      SUNNYSIDE NEIGHBORHOOD MAP                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│     NORTH DISTRICT              CENTRAL DISTRICT                        │
│     (Residential)               (Mixed Commercial)                      │
│     ┌─────────────┐             ┌─────────────┐                         │
│     │  ZONE A     │             │   ZONE B    │                         │
│     │             │             │             │                         │
│     │ Population: │             │ Population: │                         │
│     │   3,500     │             │   4,000     │                         │
│     │             │             │             │                         │
│     │ Primary:    │             │ Primary:    │                         │
│     │  Families   │             │  Students   │                         │
│     │  Seniors    │             │  Young Prof │                         │
│     └──────┬──────┘             └──────┬──────┘                         │
│            │                           │                                │
│     ───────┴───────────────────────────┴───────                         │
│                        MAIN STREET                                      │
│     ───────┬───────────────────────────┬───────                         │
│            │                           │                                │
│     ┌──────┴──────┐             ┌──────┴──────┐                         │
│     │   ZONE C    │             │   ZONE D    │                         │
│     │             │             │             │                         │
│     │ Population: │             │ Population: │                         │
│     │   2,500     │             │   2,000     │                         │
│     │             │             │             │                         │
│     │ Primary:    │             │ Primary:    │                         │
│     │  Students   │             │  Families   │                         │
│     │             │             │  Seniors    │                         │
│     └─────────────┘             └─────────────┘                         │
│     SOUTH DISTRICT              EAST DISTRICT                           │
│     (University Area)           (Suburban)                              │
│                                                                         │
│   LEGEND:                                                               │
│   ═══ Major roads (high visibility for advertising)                     │
│   ─── Secondary roads                                                   │
│   [ ] Commercial zones (permits available)                              │
│   ( ) Residential zones (special permit required)                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

#### 2.1.3.1 neighborhood info break down

| Zone            | Foot Traffic | Rent/Month | Visibility Bonus       | Primary Demographics         |
|-----------------|--------------|------------|------------------------|------------------------------|
| Zone A (North)  | Medium       | $800       | +5% family awareness   | Families, Seniors            |
| Zone B (Central)| High         | $1,200     | +15% general awareness | Students, Young Professionals|
| Zone C (South)  | High         | $1,000     | +10% student awareness | Students                     |
| Zone D (East)   | Low          | $600       | None                   | Families, Seniors            |



### 2.1.1 Sunnyside Neighborhood Profile

┌─────────────────────────────────────────────────────────────────────────┐
│                    SUNNYSIDE NEIGHBORHOOD PROFILE                       │
├─────────────────────────────────────────────────────────────────────────┤
|   #### Alignment with Real-World Demographics                           |
|    The baseline percentages are designed to approximate general         |
|    U.S. population trends:                                              |
|    • 	Students (school-age): typically 20–22%                           |
|    • 	Families (households with children): typically 30–35%             |
|    • 	Seniors (65+): typically 17–18%                                   |
|    • 	Adults ( singles, couples w/o children): typically 30–32%         |
|    The chosen distribution closely mirrors these averages,              |
|    ensuring realism while maintaining flexibility for gameplay.         |
|                                                                         |
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   GEOGRAPHY                          DEMOGRAPHICS                       │
│   ────────────                       ────────────                       │
│   Area: 2.5 square miles             Population: 16,000                 │
│   Climate: Temperate                 Households: 4,800                  │
│   Urban density: Medium              Avg. household size: 2.5           │
│                                                                         │
│   POPULATION BREAKDOWN               ECONOMIC PROFILE                   │
│   ────────────────────               ────────────────                   │
│  	Students: 25%(4,200)               Median income: $52,000             │
│  	Families: 28%(4,800)               Unemployment: 4.2%                 │
│   Seniors: 18%(3,000)                Home ownership: 45%                │
│  	Adults (non-family): 29%(5,000)    Renters: 55%                       │
│                                                                         │
│   LAUNDRY MARKET SIZE                                                   │
│   ───────────────────                                                   │
│   Weekly demand: ~2,400 loads                                           │
│   Annual market value: ~$312,000                                        │
│   Growth rate: 2% annually                                              │
│   Seasonal variation: ±15%                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

### Demographic Breakdown


### 2.1.2 Customer Segments (Detailed Profiles)

### 2.1.2.1 Segment A: Students (35% of market)

┌─────────────────────────────────────────────────────────────────────────┐
│                        STUDENT SEGMENT PROFILE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   KEY CHARACTERISTICS                                                   │
│   • Price-sensitive (primary driver)                                    │
│   • Irregular schedules (late nights, weekends)                         │
│   • Lower loyalty (switches for discounts)                              │
│   • High social media engagement                                        │
│   • Environmentally conscious (moderate)                                │
│                                                                         │
│   BEHAVIORAL PATTERNS                                                   │
│   • Average loads/week: 1.5                                             │
│   • Preferred hours: 8 PM – 12 AM                                       │
│   • Price elasticity: High (-2.5)                                       │
│   • Review likelihood: 40%                                              │
│   • Referral potential: High                                            │
│                                                                         │
│   DECISION FACTORS (WEIGHTED)                                           │
│   1. Price (40%)                                                        │
│   2. Convenience/Hours (25%)                                            │
│   3. Proximity (20%)                                                    │
│   4. Atmosphere/WiFi (10%)                                              │
│   5. Sustainability (5%)                                                │
│                                                                         │
│   SEASONAL PATTERNS                                                     │
│   • Sept–May: Full presence                                             │
│   • June–Aug: 30% reduction (summer break)                              │
│   • Finals weeks: +20% demand spike                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

### 2.1.2.2 Segment B: Families (40% of market)

┌─────────────────────────────────────────────────────────────────────────┐
│                        FAMILY SEGMENT PROFILE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   KEY CHARACTERISTICS                                                   │
│   • Quality-focused (clean, safe environment)                           │
│   • Schedule-driven (weekends, early evenings)                          │
│   • Higher loyalty (values consistency)                                 │
│   • Moderate price sensitivity                                          │
│   • Values child-friendly amenities                                     │
│                                                                         │
│   BEHAVIORAL PATTERNS                                                   │
│   • Average loads/week: 3.5                                             │
│   • Preferred hours: 9 AM – 6 PM (weekends peak)                        │
│   • Price elasticity: Medium (-1.2)                                     │
│   • Review likelihood: 60%                                              │
│   • Referral potential: Medium (word-of-mouth)                          │
│                                                                         │
│   DECISION FACTORS (WEIGHTED)                                           │
│   1. Cleanliness/Safety (35%)                                           │
│   2. Reliability (25%)                                                  │
│   3. Proximity (20%)                                                    │
│   4. Price (15%)                                                        │
│   5. Family amenities (5%)                                              │
│                                                                         │
│   SEASONAL PATTERNS                                                     │
│   • Back-to-school (Aug–Sept): +25% demand                              │
│   • Holidays: +15% demand (guests, events)                              │
│   • Summer: Stable                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
  
### 2.1.2.3 Segment C: Seniors (25% of market)

┌─────────────────────────────────────────────────────────────────────────┐
│                        SENIOR SEGMENT PROFILE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   KEY CHARACTERISTICS                                                   │
│   • Service-focused (values personal attention)                         │
│   • Fixed income (moderate price sensitivity)                           │
│   • Extremely high loyalty (rarely switches)                            │
│   • Prefers daytime hours                                               │
│   • Values accessibility and assistance                                 │
│                                                                         │
│   BEHAVIORAL PATTERNS                                                   │
│   • Average loads/week: 2.0                                             │
│   • Preferred hours: 7 AM – 2 PM (weekdays)                             │
│   • Price elasticity: Low (-0.8)                                        │
│   • Review likelihood: 25% (but highly detailed)                        │
│   • Referral potential: High (senior networks)                          │
│                                                                         │
│   DECISION FACTORS (WEIGHTED)                                           │
│   1. Customer service (40%)                                             │
│   2. Accessibility (25%)                                                │
│   3. Proximity (20%)                                                    │
│   4. Price (10%)                                                        │
│   5. Familiar faces/consistency (5%)                                    │
│                                                                         │
│   SEASONAL PATTERNS                                                     │
│   • Winter: -15% (mobility challenges)                                  │
│   • Spring/Fall: Peak activity                                          │
│   • Holidays: -10% (family visits)                                      │
│                                                                         │
│   SPECIAL CONSIDERATIONS                                                │
│   • Senior discount expectation: 10-15%                                 │
│   • Assistance requests: Folding, carrying                              │
│   • Complaint style: Direct, in-person                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

### 2.1.2.4 Segment D: Adults (25% of market)

┌─────────────────────────────────────────────────────────────────────────┐
│                        ADULT SEGMENT PROFILE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   KEY CHARACTERISTICS                                                   │
│   • Convenience-driven (values speed and efficiency)                    │
│   • Dual-income households or working professionals                     │
│   • Moderate loyalty (switches for better deals or convenience)         │
│   • Balances work and family schedules                                  │
│   • Tech-comfortable (uses apps, online booking)                        │
│                                                                         │
│   BEHAVIORAL PATTERNS                                                   │
│   • Average loads/week: 3.5                                             │
│   • Preferred hours: 5 PM – 9 PM (weekdays), flexible weekends          │
│   • Price elasticity: Moderate (-1.2)                                   │
│   • Review likelihood: 40% (short, efficiency-focused)                  │
│   • Referral potential: Moderate (friends, coworkers)                   │
│                                                                         │
│   DECISION FACTORS (WEIGHTED)                                           │
│   1. Convenience/speed (35%)                                            │
│   2. Price (25%)                                                        │
│   3. Proximity (20%)                                                    │
│   4. Customer service (15%)                                             │
│   5. Loyalty programs (5%)                                              │
│                                                                         │
│   SEASONAL PATTERNS                                                     │
│   • Summer: +10% (lighter schedules, more activity)                     │
│   • Fall: Stable (school/work routines)                                 │
│   • Holidays: +20% (family gatherings, increased demand)                │
│                                                                         │
│   SPECIAL CONSIDERATIONS                                                │
│   • Value bundle deals and family packages                              │
│   • Expect digital convenience (apps, reminders, autopay)               │
│   • Complaint style: Online reviews or quick calls                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

#### 2.1.2.5 Segment E: Young Adults / Professionals (20% of market)

┌─────────────────────────────────────────────────────────────────────────┐
│                 YOUNG ADULT / PROFESSIONAL SEGMENT PROFILE              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   KEY CHARACTERISTICS                                                    │
│   • Career-focused (values efficiency and reliability)                   │
│   • Moderate price sensitivity (balances budget with quality)            │
│   • Seeks modern, tech-enabled experiences                               │
│   • Builds loyalty through perks and consistency                         │
│   • Socially active, values networking opportunities                     │
│                                                                          │
│   BEHAVIORAL PATTERNS                                                    │
│   • Average loads/week: 2.5                                              │
│   • Preferred hours: 6 PM – 10 PM (weekdays), flexible weekends          │
│   • Price elasticity: Moderate (-1.5)                                    │
│   • Review likelihood: 35% (balanced, professional tone)                 │
│   • Referral potential: High (peer groups, workplace networks)           │
│                                                                          │
│   DECISION FACTORS (WEIGHTED)                                            │
│   1. Convenience/speed (30%)                                             │
│   2. Price (25%)                                                         │
│   3. Quality/reliability (20%)                                           │
│   4. Proximity (15%)                                                     │
│   5. Perks/loyalty programs (10%)                                        │
│                                                                          │
│   SEASONAL PATTERNS                                                      │
│   • Summer: +15% (more social activity, flexible schedules)              │
│   • Winter: Stable (work routines dominate)                              │
│   • Holidays: +10% (gift-giving, social gatherings)                      │
│                                                                          │
│   SPECIAL CONSIDERATIONS                                                 │
│   • Expect digital convenience (apps, autopay, notifications)            │
│   • Value professional, modern branding                                  │
│   • Complaint style: Online reviews, email, or social media posts        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘



