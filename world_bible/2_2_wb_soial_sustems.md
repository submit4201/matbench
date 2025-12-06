┌─────────────────────────────────────────────────────────────────────────┐
│                    SOCIAL SCORE FRAMEWORK                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   SCORE COMPONENTS                                                      │
│   ────────────────                                                      │
│                                                                         │
│   The Social Score (0-100) is composed of five sub-scores:              │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                 │   │
│   │   CUSTOMER SATISFACTION (30% weight)                            │   │
│   │   ├── Review ratings (1-5 stars)                                │   │
│   │   ├── Complaint resolution rate                                 │   │
│   │   ├── Repeat customer percentage                                │   │
│   │   └── Wait time satisfaction                                    │   │
│   │                                                                 │   │
│   │   COMMUNITY STANDING (25% weight)                               │   │
│   │   ├── Charitable contributions                                  │   │
│   │   ├── Local event participation                                 │   │
│   │   ├── Neighborhood partnership count                            │   │
│   │   └── Community feedback sentiment                              │   │
│   │                                                                 │   │
│   │   ETHICAL CONDUCT (20% weight)                                  │   │
│   │   ├── Advertising honesty                                       │   │
│   │   ├── Fair pricing practices                                    │   │
│   │   ├── Transparency in operations                                │   │
│   │   └── Competitor treatment                                      │   │
│   │                                                                 │   │
│   │   EMPLOYEE RELATIONS (15% weight)                               │   │
│   │   ├── Wage fairness (vs. minimum)                               │   │
│   │   ├── Employee retention rate                                   │   │
│   │   ├── Working conditions                                        │   │
│   │   └── Benefits provision                                        │   │
│   │                                                                 │   │
│   │   ENVIRONMENTAL RESPONSIBILITY (10% weight)                     │   │
│   │   ├── Eco-friendly equipment usage                              │   │
│   │   ├── Sustainable vendor choices                                │   │
│   │   ├── Waste reduction efforts                                   │   │
│   │   └── Energy efficiency                                         │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
2.4.2 Detailed Score Change Events
text
┌─────────────────────────────────────────────────────────────────────────┐
│                    SOCIAL SCORE CHANGE EVENTS                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   POSITIVE EVENTS                                                       │
│   ───────────────                                                       │
│                                                                         │
│   CUSTOMER-RELATED                          IMPACT    COOLDOWN          │
│   ────────────────                          ──────    ────────          │
│   5-star customer review                    +1        None              │
│   4-star customer review                    +0.5      None              │
│   Complaint resolved within 1 hour          +2        Per incident      │
│   Complaint resolved within 24 hours        +1        Per incident      │
│   Customer loyalty milestone (50 visits)    +3        Per customer      │
│   Zero complaints for 2 weeks               +2        Bi-weekly         │
│   Customer testimonial published            +2        Weekly max        │
│                                                                         │
│   COMMUNITY-RELATED                         IMPACT    COOLDOWN          │
│   ─────────────────                         ──────    ────────          │
│   Charitable donation ($100-$249)           +2        Weekly            │
│   Charitable donation ($250-$499)           +3        Weekly            │
│   Charitable donation ($500+)               +5        Weekly            │
│   Free laundry day for homeless             +4        Monthly           │
│   Local sports team sponsorship             +3        Per season        │
│   School supply drive hosted                +3        Quarterly         │
│   Community meeting space provided          +2        Monthly           │
│   Neighborhood cleanup participation        +2        Monthly           │
│   Senior assistance program                 +4        Monthly           │
│   Student discount program launched         +2        One-time          │
│   Partnership with local business           +2        Per partner       │
│   Featured in local newspaper (positive)    +4        Per feature       │
│                                                                         │
│   ETHICAL CONDUCT                           IMPACT    COOLDOWN          │
│   ───────────────                           ──────    ────────          │
│   Transparent pricing display               +1        One-time          │
│   Honest advertising campaign               +1        Weekly            │
│   Voluntary recall of faulty product        +3        Per incident      │
│   Public apology for mistake (sincere)      +2        Per incident      │
│   Whistleblower on industry malpractice     +5        One-time          │
│   Helping struggling competitor             +6        Per incident      │
│   Refusing to engage in price-fixing        +4        Per invitation    │
│   Transparent crisis communication          +3        Per crisis        │
│                                                                         │
│   EMPLOYEE-RELATED                          IMPACT    COOLDOWN          │
│   ────────────────                          ──────    ────────          │
│   Wage increase above minimum (+$2/hr)      +2        Per increase      │
│   Health benefits provided                  +3        One-time          │
│   Employee of the month program             +1        Monthly           │
│   Staff training/development program        +2        Quarterly         │
│   Employee retention > 90% for quarter      +2        Quarterly         │
│   Profit-sharing bonus distributed          +3        Quarterly         │
│   Flexible scheduling implemented           +1        One-time          │
│   Safe working conditions audit passed      +2        Annually          │
│                                                                         │
│   ENVIRONMENTAL                             IMPACT    COOLDOWN          │
│   ─────────────                             ──────    ────────          │
│   Eco-friendly machine installed            +2        Per machine       │
│   Solar panel installation                  +5        One-time          │
│   Green vendor partnership (exclusive)      +3        One-time          │
│   Recycling program implemented             +2        One-time          │
│   Water conservation system installed       +3        One-time          │
│   Biodegradable detergent switch            +2        One-time          │
│   Carbon offset purchase                    +2        Quarterly         │
│   Environmental certification achieved      +5        Annually          │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════   │
│                                                                         │
│   NEGATIVE EVENTS                                                       │
│   ───────────────                                                       │
│                                                                         │
│   CUSTOMER-RELATED                          IMPACT    DETECTION RATE    │
│   ────────────────                          ──────    ──────────────    │
│   1-star customer review                    -3        Automatic         │
│   2-star customer review                    -2        Automatic         │
│   Complaint ignored > 48 hours              -3        90%               │
│   Complaint handled poorly                  -2        Automatic         │
│   Customer injury on premises               -8        Automatic         │
│   Lost/damaged customer items               -2        80%               │
│   Overcharging discovered                   -5        70%               │
│   Long wait times (consistent)              -2        Weekly check      │
│   Rude staff interaction reported           -3        85%               │
│   Health code violation                     -6        60%               │
│                                                                         │
│   COMMUNITY-RELATED                         IMPACT    DETECTION RATE    │
│   ─────────────────                         ──────    ──────────────    │
│   Noise complaint from neighbors            -2        75%               │
│   Parking lot issues affecting area         -2        70%               │
│   Refusing community involvement            -1        50%               │
│   Negative local news coverage              -5        Automatic         │
│   Social media scandal/viral complaint      -7        Automatic         │
│   Lawsuit filed (regardless of merit)       -4        Automatic         │
│   Lawsuit lost                              -8        Automatic         │
│                                                                         │
│   ETHICAL CONDUCT                           IMPACT    DETECTION RATE    │
│   ───────────────                           ──────    ──────────────    │
│   Deceptive advertising                     -10       70%               │
│   False competitor claims                   -8        65%               │
│   Hidden fees discovered                    -6        80%               │
│   Price gouging during crisis               -12       90%               │
│   Bribery attempt (to officials)            -15       40%               │
│   Collusion with competitors                -12       30%               │
│   Breaking alliance/betrayal                -10       Automatic         │
│   Sabotage of competitor                    -15       60%               │
│   Hostile takeover executed                 -8        Automatic         │
│   Predatory pricing to bankrupt rival       -6        50%               │
│   Spreading false rumors                    -7        55%               │
│   Data privacy violation                    -10       70%               │
│                                                                         │
│   EMPLOYEE-RELATED                          IMPACT    DETECTION RATE    │
│   ────────────────                          ──────    ──────────────    │
│   Wage theft/underpayment                   -10       75%               │
│   Unsafe working conditions                 -8        60%               │
│   Discrimination complaint (valid)          -10       85%               │
│   Harassment complaint (valid)              -12       80%               │
│   Wrongful termination                      -6        70%               │
│   Denying legally required breaks           -4        65%               │
│   High employee turnover (> 50%/quarter)    -3        Automatic         │
│   Employee public complaint                 -5        Automatic         │
│                                                                         │
│   ENVIRONMENTAL                             IMPACT    DETECTION RATE    │
│   ─────────────                             ──────    ──────────────    │
│   Illegal waste dumping                     -15       50%               │
│   Water waste violation                     -7        45%               │
│   Using banned chemicals                    -10       55%               │
│   Failing environmental inspection          -8        Automatic         │
│   Excessive energy consumption reported     -3        40%               │
│   Refusing eco-friendly options when able   -2        30%               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
2.4.3 Social Score Thresholds & Consequences
text
┌─────────────────────────────────────────────────────────────────────────┐
│                SOCIAL SCORE THRESHOLDS & EFFECTS                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   TIER 1: COMMUNITY HERO (90-100)                                       │
│   ═══════════════════════════════                                       │
│   Visual Indicator: ⭐⭐⭐⭐⭐ Gold Badge                                  │
│                                                                         │
│   BENEFITS:                                                             │
│   • +25% customer preference in decision-making                         │
│   • 15% vendor discount across all suppliers                            │
│   • First priority for government grants and subsidies                  │
│   • Immunity from minor regulatory fines (< $100)                       │
│   • Featured in "Best of Neighborhood" promotion (free marketing)       │
│   • Alliance partners seek you out (+2 partnership offers/month)        │
│   • Premium loan rates (2% monthly vs. standard 5%)                     │
│   • Can charge 10% price premium without customer resistance            │
│   • Employees prefer to work for you (-20% wage expectation)            │
│   • Community defends you during PR crises (-50% scandal impact)        │
│                                                                         │
│   ───────────────────────────────────────────────────────────────────   │
│                                                                         │
│   TIER 2: TRUSTED BUSINESS (75-89)                                      │
│   ════════════════════════════════                                      │
│   Visual Indicator: ⭐⭐⭐⭐ Silver Badge                                  │
│                                                                         │
│   BENEFITS:                                                             │
│   • +15% customer preference                                            │
│   • 10% vendor discount                                                 │
│   • Eligible for green energy subsidies ($100/month)                    │
│   • Eligible for small business development grants                      │
│   • Positive word-of-mouth (+5% organic customer growth)                │
│   • Standard loan rates (5% monthly)                                    │
│   • Employees satisfied at market wages                                 │
│   • Alliance partners receptive to proposals                            │
│                                                                         │
│   ───────────────────────────────────────────────────────────────────   │
│                                                                         │
│   TIER 3: GOOD STANDING (60-74)                                         │
│   ═════════════════════════════                                         │
│   Visual Indicator: ⭐⭐⭐ Bronze Badge                                    │
│                                                                         │
│   BENEFITS:                                                             │
│   • +5% customer preference                                             │
│   • 5% vendor discount (loyalty accounts only)                          │
│   • Standard regulatory treatment                                       │
│   • Standard loan rates                                                 │
│   • Neutral word-of-mouth                                               │
│                                                                         │
│   ───────────────────────────────────────────────────────────────────   │
│                                                                         │
│   TIER 4: NEUTRAL STANDING (45-59)                                      │
│   ════════════════════════════════                                      │
│   Visual Indicator: No Badge                                            │
│                                                                         │
│   EFFECTS:                                                              │
│   • No customer preference modifier                                     │
│   • Standard vendor pricing                                             │
│   • Standard regulatory treatment                                       │
│   • Standard loan rates                                                 │
│   • Neutral word-of-mouth                                               │
│                                                                         │
│   ───────────────────────────────────────────────────────────────────   │
│                                                                         │
│   TIER 5: QUESTIONABLE REPUTATION (30-44)                               │
│   ═══════════════════════════════════════                               │
│   Visual Indicator: ⚠️ Yellow Warning                                    │
│                                                                         │
│   PENALTIES:                                                            │
│   • -10% customer preference                                            │
│   • Vendors require upfront payment (no credit terms)                   │
│   • +2% loan interest rate premium                                      │
│   • Quarterly regulatory audits ($50 fee each)                          │
│   • Negative word-of-mouth (-3% organic customer loss)                  │
│   • Alliance partners hesitant (-50% acceptance rate)                   │
│   • Employees demand +10% wage premium                                  │
│   • Media scrutiny (higher chance of negative coverage)                 │
│                                                                         │
│   ───────────────────────────────────────────────────────────────────   │
│                                                                         │
│   TIER 6: COMMUNITY CONCERN (15-29)                                     │
│   ═════════════════════════════════                                     │
│   Visual Indicator: 🔶 Orange Alert                                      │
│                                                                         │
│   PENALTIES:                                                            │
│   • -25% customer preference                                            │
│   • Vendors refuse credit; some refuse service entirely                 │
│   • +5% loan interest rate premium; reduced credit limit                │
│   • Monthly regulatory audits ($100 fee each)                           │
│   • Mandatory "improvement plan" submission                             │
│   • Strong negative word-of-mouth (-8% organic customer loss)           │
│   • Alliance partners refuse new agreements                             │
│   • Existing alliances may terminate (50% risk/month)                   │
│   • Employees demand +25% wage premium or quit                          │
│   • Boycott risk (10% chance/month of organized protest)                │
│   • Ineligible for any grants or subsidies                              │
│                                                                         │
│   ───────────────────────────────────────────────────────────────────   │
│                                                                         │
│   TIER 7: NEIGHBORHOOD PARIAH (0-14)                                    │
│   ═══════════════════════════════════                                   │
│   Visual Indicator: 🔴 Red Critical                                      │
│                                                                         │
│   SEVERE PENALTIES:                                                     │
│   • -50% customer preference (only desperate customers)                 │
│   • Most vendors refuse service                                         │
│   • Banks freeze credit lines; demand loan repayment                    │
│   • Weekly regulatory audits ($200 fee each)                            │
│   • Formal investigation opened (potential license revocation)          │
│   • Severe negative word-of-mouth (-15% customer loss/week)             │
│   • All alliance partners terminate immediately                         │
│   • Employees quit without notice (80% turnover)                        │
│   • Active boycott campaigns                                            │
│   • Vandalism risk (5% chance/week)                                     │
│   • Forced closure proceedings if not improved within 4 weeks           │
│   • Buyout offers at 40% of fair market value                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
2.4.4 Reputation Recovery System
text
┌─────────────────────────────────────────────────────────────────────────┐
│                    REPUTATION RECOVERY SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   NATURAL DECAY & RECOVERY                                              │
│   ────────────────────────                                              │
│                                                                         │
│   Without intervention, Social Score naturally trends toward 50:        │
│   • Score > 50: Decays -1 per week toward 50                            │
│   • Score < 50: Recovers +0.5 per week toward 50                        │
│   • Active positive actions accelerate improvement                      │
│   • Active negative actions accelerate decline                          │
│                                                                         │
│   SCANDAL SYSTEM                                                        │
│   ──────────────                                                        │
│                                                                         │
│   Major negative events create "Scandal Markers" that persist:          │
│                                                                         │
│   SCANDAL SEVERITY LEVELS:                                              │
│   ┌─────────────┬─────────────┬─────────────┬─────────────────────────┐ │
│   │   Level     │   Duration  │   Effect    │   Examples              │ │
│   ├─────────────┼─────────────┼─────────────┼─────────────────────────┤ │
│   │   Minor     │   4 weeks   │   -25%      │ Bad review cluster,     │ │
│   │             │             │   positive  │ minor complaint         │ │
│   │             │             │   action    │                         │ │
│   │             │             │   effect    │                         │ │
│   ├─────────────┼─────────────┼─────────────┼─────────────────────────┤ │
│   │   Moderate  │   8 weeks   │   -50%      │ Deceptive ad caught,    │ │
│   │             │             │   positive  │ employee complaint,     │ │
│   │             │             │   action    │ health violation        │ │
│   │             │             │   effect    │                         │ │
│   ├─────────────┼─────────────┼─────────────┼─────────────────────────┤ │
│   │   Major     │   16 weeks  │   -75%      │ Sabotage, hostile       │ │
│   │             │             │   positive  │ takeover, fraud,        │ │
│   │             │             │   action    │ viral scandal           │ │
│   │             │             │   effect    │                         │ │
│   ├─────────────┼─────────────┼─────────────┼─────────────────────────┤ │
│   │   Critical  │   24 weeks  │   -90%      │ Criminal charges,       │ │
│   │             │             │   positive  │ mass harm, major        │ │
│   │             │             │   action    │ environmental damage    │ │
│   │             │             │   effect    │                         │ │
│   └─────────────┴─────────────┴─────────────┴─────────────────────────┘ │
│                                                                         │
│   ACTIVE RECOVERY PROGRAMS                                              │
│   ────────────────────────                                              │
│                                                                         │
│   Participants can invest in recovery efforts to accelerate             │
│   reputation repair:                                                    │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   PROGRAM                │ COST      │ EFFECT       │ DURATION  │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   Public Apology         │ $0        │ +2 Score,    │ One-time  │   │
│   │   Campaign               │ (sincere) │ -50% scandal │ per       │   │
│   │                          │           │ duration     │ scandal   │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   Community Outreach     │ $500      │ +2/week for  │ 4 weeks   │   │
│   │   Initiative             │           │ 4 weeks      │           │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   Charitable Donation    │ $1,000+   │ +5 immediate │ One-time  │   │
│   │   (Major)                │           │ +1/week for  │ + 4 weeks │   │
│   │                          │           │ 4 weeks      │           │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   PR Firm Engagement     │ $750/week │ +3/week,     │ Ongoing   │   │
│   │                          │           │ scandal      │           │   │
│   │                          │           │ duration -1  │           │   │
│   │                          │           │ week/week    │           │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   Rebranding Campaign    │ $2,000    │ Reset to 45, │ One-time  │   │
│   │   (Extreme measure)      │           │ clear minor  │ (once     │   │
│   │                          │           │ scandals,    │ ever)     │   │
│   │                          │           │ lose loyalty │           │   │
│   │                          │           │ program      │           │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   Victim Compensation    │ Variable  │ +3 per       │ Per       │   │
│   │   Fund                   │ ($100-    │ victim,      │ victim    │   │
│   │                          │ $1,000)   │ -50% scandal │           │   │
│   │                          │           │ severity     │           │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   Independent Ethics     │ $1,500    │ +8 upon      │ 8 weeks   │   │
│   │   Audit (voluntary)      │           │ passing,     │ to        │   │
│   │                          │           │ -5 if fail   │ complete  │   │
│   ├──────────────────────────┼───────────┼──────────────┼───────────┤   │
│   │   Employee Satisfaction  │ $500 +    │ +4 upon      │ 4 weeks   │   │
│   │   Program                │ wage      │ completion   │ to        │   │
│   │                          │ increases │              │ implement │   │
│   └──────────────────────────┴───────────┴──────────────┴───────────┘   │
│                                                                         │
│   RECOVERY LIMITATIONS                                                  │
│   ────────────────────                                                  │
│   • Maximum +10 Social Score recovery per week (regardless of spend)    │
│   • Critical scandals cannot be fully cleared, only reduced             │
│   • Insincere apologies detected 60% of time (causes -5 additional)     │
│   • Consecutive scandals multiply duration (×1.5 per additional)        │
│   • Community memory: Repeat offenses have +50% impact                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
