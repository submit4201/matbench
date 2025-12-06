2.5.3 Supply Chain Events & Disruptions
text
┌─────────────────────────────────────────────────────────────────────────┐
│                 SUPPLY CHAIN EVENTS & DISRUPTIONS                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   REGULAR SUPPLY CHAIN EVENTS                                           │
│   ═══════════════════════════                                           │
│                                                                         │
│   These events occur randomly throughout the simulation:                │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   EVENT                │ PROBABILITY │ EFFECT         │DURATION │   │
│   ├────────────────────────┼─────────────┼────────────────┼─────────┤   │
│   │   Delivery Delay       │ 10%/order   │ +3-5 days      │ One-time│   │
│   │   (minor)              │             │ delivery time  │         │   │
│   ├────────────────────────┼─────────────┼────────────────┼─────────┤   │
│   │   Delivery Delay       │ 5%/order    │ +7-14 days     │ One-time│   │
│   │   (major)              │             │ delivery time  │         │   │
│   ├────────────────────────┼─────────────┼────────────────┼─────────┤   │
│   │   Partial Shipment     │ 8%/order    │ Only 50-75%    │ One-time│   │
│   │                        │             │ of order       │         │   │
│   │                        │             │ arrives        │         │   │
│   ├────────────────────────┼─────────────┼────────────────┼─────────┤   │
│   │   Quality Issue        │ 5%/order    │ 20% of         │ One-time│   │
│   │   (minor)              │             │ product        │         │   │
│   │                        │             │ defective      │         │   │
│   ├────────────────────────┼─────────────┼────────────────┼─────────┤   │
│   │   Quality Issue        │ 2%/order    │ 50%+ product   │ One-time│   │
│   │   (major)              │             │ defective,     │         │   │
│   │                        │             │ recall needed  │         │   │
│   ├────────────────────────┼─────────────┼────────────────┼─────────┤   │
│   │   Price Fluctuation    │ 15%/month   │ ±5-15% price   │ 2-4 wks │   │
│   │   (normal)             │             │ change         │         │   │
│   ├────────────────────────┼─────────────┼────────────────┼─────────┤   │
│   │   Lost Shipment        │ 1%/order    │ Order never    │ One-time│   │
│   │                        │             │ arrives, must  │         │   │
│   │                        │             │ reorder        │         │   │
│   └────────────────────────┴─────────────┴────────────────┴─────────┘   │
│                                                                         │
│   MAJOR SUPPLY CHAIN DISRUPTIONS                                        │
│ ext
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   EVENT: VENDOR SHORTAGE                                        │   │
│   │   ─────────────────────                                         │   │
│   │   Probability:     5% per week                                  │   │
│   │   Duration:        2-4 weeks                                    │   │
│   │   Affected:        1-2 random vendors                           │   │
│   │                                                                 │   │
│   │   Effects:                                                      │   │
│   │   • Affected vendor can only fulfill 50% of orders              │   │
│   │   • Prices increase 20-30% during shortage                      │   │
│   │   • New customers rejected by affected vendor                   │   │
│   │   • Strategic Partners get priority fulfillment                 │   │
│   │                                                                 │   │
│   │   Response Options:                                             │   │
│   │   • Switch to alternate vendor (lose relationship progress)     │   │
│   │   • Pay premium for emergency supply (+50% cost)                │   │
│   │   • Reduce operations until shortage ends                       │   │
│   │   • Use existing inventory buffer                               │   │
│   │                                                                 │   │
│   │   Strategic Implications:                                       │   │
│   │   • Tests inventory management foresight                        │   │
│   │   • Rewards multi-vendor relationships                          │   │
│   │   • Higher tier relationships provide protection                │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   EVENT: PRICE SPIKE                                            │   │
│   │   ──────────────────                                            │   │
│   │   Probability:     8% per week                                  │   │
│   │   Duration:        2-6 weeks                                    │   │
│   │   Affected:        All vendors in category or specific vendor   │   │
│   │                                                                 │   │
│   │   Severity Levels:                                              │   │
│   │   • Minor:    +10-20% price increase                            │   │
│   │   • Moderate: +20-40% price increase                            │   │
│   │   • Severe:   +40-75% price increase                            │   │
│   │                                                                 │   │
│   │   Causes (flavor text):                                         │   │
│   │   • Raw material shortage                                       │   │
│   │   • Transportation cost increase                                │   │
│   │   • Regulatory compliance costs                                 │   │
│   │   • Currency fluctuation                                        │   │
│   │   • Natural disaster affecting production                       │   │
│   │                                                                 │   │
│   │   Response Options:                                             │   │
│   │   • Absorb cost increase (reduce margins)                       │   │
│   │   • Pass cost to customers (risk losing price-sensitive)        │   │
│   │   • Switch vendors (if alternative available)                   │   │
│   │   • Reduce supply usage (eco-mode, less detergent)              │   │
│   │   • Negotiate with vendor (relationship-dependent)              │   │
│   │                                                                 │   │
│   │   Tier Benefits:                                                │   │
│   │   • Strategic Partners: Price locked for 90 days                │   │
│   │   • Preferred Customers: 50% of price increase                  │   │
│   │   • Regular Customers: 75% of price increase                    │   │
│   │   • New Customers: Full price increase                          │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   EVENT: VENDOR BANKRUPTCY                                      │   │
│   │   ────────────────────────                                      │   │
│   │   Probability:     1% per quarter (per vendor)                  │   │
│   │   Duration:        Permanent                                    │   │
│   │   Warning Signs:   Declining reliability, delayed payments      │   │
│   │                                                                 │   │
│   │   Effects:                                                      │   │
│   │   • Vendor immediately unavailable                              │   │
│   │   • Outstanding orders canceled (refund in 4-8 weeks)           │   │
│   │   • Prepaid inventory lost (partial insurance claim possible)   │   │
│   │   • Must establish new vendor relationship from Tier 1          │   │
│   │                                                                 │   │
│   │   Warning System:                                               │   │
│   │   • 4 weeks before: Rumors in industry (50% detection)          │   │
│   │   • 2 weeks before: Delayed shipments increase                  │   │
│   │   • 1 week before: Payment terms change to prepay only          │   │
│   │                                                                 │   │
│   │   Response Options:                                             │   │
│   │   • Preemptively switch vendors when warnings detected          │   │
│   │   • Build inventory buffer                                      │   │
│   │   • File insurance claim (if coverage purchased)                │   │
│   │   • Emergency orders from alternate vendors                     │   │
│   │                                                                 │   │
│   │   Insurance:                                                    │   │
│   │   • Supply chain insurance: $75/month                           │   │
│   │   • Covers: 80% of lost prepaid orders                          │   │
│   │   • Covers: Emergency supply cost difference (up to $500)       │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   EVENT: QUALITY RECALL                                         │   │
│   │   ─────────────────────                                         │   │
│   │   Probability:     3% per month (per vendor)                    │   │
│   │   Duration:        1-3 weeks                                    │   │
│   │   Affected:        Specific product batch                       │   │
│   │                                                                 │   │
│   │   Effects:                                                      │   │
│   │   • Must dispose of affected inventory                          │   │
│   │   • Customer complaints if used before recall                   │   │
│   │   • Social Score impact if customers harmed                     │   │
│   │   • Vendor provides partial refund (50-100%)                    │   │
│   │                                                                 │   │
│   │   Severity Levels:                                              │   │
│   │   ┌───────────┬──────────────────┬─────────────┬───────────────┐│   │
│   │   │  Level    │  Customer Impact │ Refund Rate │ Social Score  ││   │
│   │   ├───────────┼──────────────────┼─────────────┼───────────────┤│   │
│   │   │  Minor    │  Mild irritation │ 75%         │ -1 if used    ││   │
│   │   │  Moderate │  Skin irritation │ 100%        │ -3 if used    ││   │
│   │   │  Severe   │  Allergic react. │ 100% + $200 │ -8 if used    ││   │
│   │   │  Critical │  Health hazard   │ 150% + $500 │ -15 if used   ││   │
│   │   └───────────┴──────────────────┴─────────────┴───────────────┘│   │
│   │                                                                 │   │
│   │   Response Options:                                             │   │
│   │   • Immediately stop using affected product                     │   │
│   │   • Proactive customer notification (+2 Social Score)           │   │
│   │   • Offer compensation to affected customers                    │   │
│   │   • Public statement distancing from vendor                     │   │
│   │   • Switch vendors (relationship impact)                        │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   EVENT: TRANSPORTATION DISRUPTION                              │   │
│   │   ────────────────────────────────                              │   │
│   │   Probability:     3% per month                                 │   │
│   │   Duration:        1-4 weeks                                    │   │
│   │   Affected:        All vendors (neighborhood-wide)              │   │
│   │                                                                 │   │
│   │   Causes:                                                       │   │
│   │   • Road construction                                           │   │
│   │   • Fuel shortage                                               │   │
│   │   • Weather emergency                                           │   │
│   │   • Labor strike                                                │   │
│   │   • Infrastructure failure                                      │   │
│   │                                                                 │   │
│   │   Effects:                                                      │   │
│   │   • All delivery times extended +5-10 days                      │   │
│   │   • Delivery costs increase 25-50%                              │   │
│   │   • Emergency orders may be impossible                          │   │
│   │   • Local suppliers (LocalSupply) less affected                 │   │
│   │                                                                 │   │
│   │   Strategic Implications:                                       │   │
│   │   • Rewards participants with inventory buffers                 │   │
│   │   • LocalSupply relationship becomes valuable                   │   │
│   │   • Tests crisis management capabilities                        │   │
│   │   • May create temporary competitive advantages                 │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   EVENT: REGULATORY CHANGE                                      │   │
│   │   ────────────────────────                                      │   │
│   │   Probability:     2% per month                                 │   │
│   │   Duration:        Permanent (new regulation)                   │   │
│   │   Notice Period:   2-4 weeks before enforcement                 │   │
│   │                                                                 │   │
│   │   Types of Changes:                                             │   │
│   │   • Banned ingredient (certain products unavailable)            │   │
│   │   • New labeling requirements (vendor costs increase)           │   │
│   │   • Environmental standards (some vendors non-compliant)        │   │
│   │   • Safety requirements (equipment upgrades needed)             │   │
│   │                                                                 │   │
│   │   Effects by Type:                                              │   │
│   │   ┌─────────────────┬───────────────────────────────────────────┐   │
│   │   │  Regulation     │  Impact                                   │   │
│   │   ├─────────────────┼───────────────────────────────────────────┤   │
│   │   │  Banned         │  MegaChem products unavailable,           │   │
│   │   │  Ingredient     │  must switch vendors                      │   │
│   │   ├─────────────────┼───────────────────────────────────────────┤   │
│   │   │  Eco Standards  │  Non-eco vendors +15% cost for            │   │
│   │   │                 │  compliance, GreenClean unaffected        │   │
│   │   ├─────────────────┼───────────────────────────────────────────┤   │
│   │   │  Safety Reqs    │  $500-$2,000 equipment upgrade            │   │
│   │   │                 │  required within 4 weeks                  │   │
│   │   ├─────────────────┼───────────────────────────────────────────┤   │
│   │   │  Labeling       │  All vendors +5% cost increase            │   │
│   │   │                 │  for 8 weeks during transition            │   │
│   │   └─────────────────┴───────────────────────────────────────────┘   │
│   │                                                                 │   │
│   │   Compliance Requirements:                                      │   │
│   │   • Must comply by deadline or face fines ($100-$500/week)      │   │
│   │   • Continued non-compliance: Social Score -5/week              │   │
│   │   • Severe non-compliance: Forced temporary closure             │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   INVENTORY MANAGEMENT SYSTEM                                           │
│   ═══════════════════════════                                           │
│                                                                         │
│   Effective supply chain management requires inventory planning:        │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   INVENTORY METRICS                                             │   │
│   │   ─────────────────                                             │   │
│   │                                                                 │   │
│   │   Stock Level:         Current inventory (in loads)             │   │
│   │   Burn Rate:           Average usage per day                    │   │
│   │   Days of Supply:      Stock Level ÷ Burn Rate                  │   │
│   │   Reorder Point:       Minimum stock before reordering          │   │
│   │   Safety Stock:        Buffer for unexpected demand/delays      │   │
│   │   Lead Time:           Days from order to delivery              │   │
│   │                                                                 │   │
│   │   RECOMMENDED INVENTORY LEVELS                                  │   │
│   │   ───────────────────────────                                   │   │
│   │                                                                 │   │
│   │   ┌─────────────────┬─────────────┬─────────────┬─────────────┐ │   │
│   │   │  Risk Tolerance │ Days Supply │ Safety Stock│ Reorder Pt  │ │   │
│   │   ├─────────────────┼─────────────┼─────────────┼─────────────┤ │   │
│   │   │  Aggressive     │ 7 days      │ 2 days      │ 5 days      │ │   │
│   │   │  Moderate       │ 14 days     │ 5 days      │ 9 days      │ │   │
│   │   │  Conservative   │ 21 days     │ 7 days      │ 14 days     │ │   │
│   │   │  Very Safe      │ 30 days     │ 10 days     │ 20 days     │ │   │
│   │   └─────────────────┴─────────────┴─────────────┴─────────────┘ │   │
│   │                                                                 │   │
│   │   INVENTORY COSTS                                               │   │
│   │   ───────────────                                               │   │
│   │                                                                 │   │
│   │   Holding Cost:        $0.01/load/week (storage, spoilage)      │   │
│   │   Stockout Cost:       Lost revenue + customer dissatisfaction  │   │
│   │   Rush Order Premium:  +50-100% of normal price                 │   │
│   │   Spoilage Rate:       1% per month (some products)             │   │
│   │                                                                 │   │
│   │   STOCKOUT CONSEQUENCES                                         │   │
│   │   ─────────────────────                                         │   │
│   │                                                                 │   │
│   │   ─────────────────────                                         │   │
│   │                                                                 │   │
│   │   • Cannot serve customers (100% revenue loss during stockout)  │   │
│   │   • Customers go to competitors (30% may not return)            │   │
│   │   • Social Score -2 per day of stockout                         │   │
│   │   • Negative reviews likely (40% chance per affected customer)  │   │
│   │   • Staff idle but still paid                                   │   │
│   │   • Reputation damage compounds with duration                   │   │
│   │                                                                 │   │
│   │   Stockout Duration Impact:                                     │   │
│   │   ┌─────────────────┬───────────────────────────────────────┐   │   │
│   │   │  Duration       │  Cumulative Impact                    │   │   │
│   │   ├─────────────────┼───────────────────────────────────────┤   │   │
│   │   │  1 day          │  Minor inconvenience, few notice      │   │   │
│   │   │  2-3 days       │  Customer complaints begin            │   │   │
│   │   │  4-7 days       │  Local news may cover, -5 Social      │   │   │
│   │   │  1-2 weeks      │  Significant customer exodus, -15     │   │   │
│   │   │  2+ weeks       │  Business viability threatened        │   │   │
│   │   └─────────────────┴───────────────────────────────────────┘   │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
