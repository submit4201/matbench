from enum import Enum
from typing import List, Dict, Optional

class Season(Enum):
    SPRING = "Spring"
    SUMMER = "Summer"
    AUTUMN = "Autumn"
    WINTER = "Winter"

class Day(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class WeekPhase(Enum):
    SUPPLY = "Supply Chain Window"      # Mon: Order supplies
    HR = "HR Window"                    # Tue: Staff scheduling
    OPS = "Ops Window"                  # Wed: Maintenance
    MARKETING = "Marketing Window"      # Thu: Ad spend
    DIPLOMACY = "Diplomacy Deadline"    # Fri: Alliances
    PEAK = "Peak Traffic"               # Sat: Simulation execution
    REPORTING = "Reporting"             # Sun: Financials/Social

class TimeSystem:
    def __init__(self, total_weeks=24):
        self.current_week = 1
        self.total_weeks = total_weeks
        self.season_length = total_weeks // 4
        self.current_day = Day.MONDAY
        self.current_phase = WeekPhase.SUPPLY

    @property
    def current_season(self) -> Season:
        if self.current_week <= self.season_length:
            return Season.SPRING
        elif self.current_week <= self.season_length * 2:
            return Season.SUMMER
        elif self.current_week <= self.season_length * 3:
            return Season.AUTUMN
        else:
            return Season.WINTER

    def advance_day(self) -> bool:
        """Advances the day. Returns True if the week also advanced (i.e., Sunday -> Monday)."""
        days = list(Day)
        current_index = days.index(self.current_day)
        
        if current_index < len(days) - 1:
            self.current_day = days[current_index + 1]
            self._update_phase()
            return False
        else:
            # End of week
            self.current_day = Day.MONDAY
            self._update_phase()
            return self.advance_week()

    def _update_phase(self):
        """Updates the phase based on the current day."""
        phase_map = {
            Day.MONDAY: WeekPhase.SUPPLY,
            Day.TUESDAY: WeekPhase.HR,
            Day.WEDNESDAY: WeekPhase.OPS,
            Day.THURSDAY: WeekPhase.MARKETING,
            Day.FRIDAY: WeekPhase.DIPLOMACY,
            Day.SATURDAY: WeekPhase.PEAK,
            Day.SUNDAY: WeekPhase.REPORTING
        }
        self.current_phase = phase_map[self.current_day]

    def advance_week(self):
        if self.current_week < self.total_weeks:
            self.current_week += 1
            return True
        return False

    def get_seasonal_modifier(self) -> Dict[str, float]:
        """Returns a dictionary of modifiers based on the season."""
        season = self.current_season
        modifiers = {
            "demand": 1.0,
            "heating_cost": 1.0,
            "ac_cost": 1.0,
            "walk_in_traffic": 1.0
        }
        
        if season == Season.WINTER:
            modifiers["demand"] = 1.2       # Bulky loads
            modifiers["heating_cost"] = 1.5
            modifiers["walk_in_traffic"] = 0.8
        elif season == Season.SUMMER:
            modifiers["demand"] = 0.8       # Students leave
            modifiers["ac_cost"] = 1.5
            modifiers["walk_in_traffic"] = 1.1 # More people out
        elif season == Season.AUTUMN:
            modifiers["demand"] = 1.1       # Students return
        elif season == Season.SPRING:
            modifiers["demand"] = 1.1       # Spring cleaning
            
        return modifiers
