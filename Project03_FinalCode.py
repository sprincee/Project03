
# Project Code (version 1.1)

from abc import ABC, abstractmethod
from datetime import datetime
import calendar
import html
from typing import Dict, List, Optional


class AvailStatus:
    PREFERRED = 'preferred'
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'

class ScheduleFormatter(ABC):
    @abstractmethod
    def format_schedule(self, schedule: Dict, month: int, year: int) -> str:
        pass

class HTMLScheduleFormatter(ScheduleFormatter):
    def format_schedule(self, schedule: Dict, month: int, year: int) -> str:
        cal = calendar.HTMLCalendar()
        html_content = [
            '''
            <table border="1" cellpadding="4" cellspacing="0" class="calendar">
                <tr>
                    <th colspan="7" class="month">
                        {month_name} {year}
                    </th>
                </tr>
                <tr>
                    <th>Mon</th>
                    <th>Tue</th>
                    <th>Wed</th>
                    <th>Thu</th>
                    <th>Fri</th>
                    <th>Sat</th>
                    <th>Sun</th>
                </tr>
            '''.format(month_name=calendar.month_name[month], year=year)
        ]

        for week in cal.monthdays2calendar(year, month):
            html_content.append('<tr>')
            
            for day, weekday in week:
                if day == 0:
                    html_content.append('<td class="noday">&nbsp;</td>')
                else:
                    date = f"{year}-{month:02d}-{day:02d}"
                    shifts = schedule.get(date, {"AM": "No coverage", "PM": "No coverage"})
                    
                    day_cell = f'''
                        <td class="day-cell">
                            <div class="day">{day}</div>
                            <div class="shifts">
                                AM: {shifts["AM"]}<br>
                                PM: {shifts["PM"]}
                            </div>
                        </td>
                    '''
                    html_content.append(day_cell)
            
            html_content.append('</tr>')
        
        html_content.append('</table>')
        
        return ''.join(html_content)

    def format_pay_report(self, pay_data: Dict) -> str:
        html_content = [
            '<table border="1" cellpadding="4" cellspacing="0">',
            '''
                <tr>
                    <th>Name</th>
                    <th>Hours</th>
                    <th>Rate</th>
                    <th>Weekly Pay</th>
                    <th>Monthly Pay</th>
                </tr>
            '''
        ]

        total_weekly = 0
        total_monthly = 0

        for name, data in pay_data.items():
            weekly_pay = data['hours'] * data['rate']
            monthly_pay = weekly_pay * 4
            total_weekly += weekly_pay
            total_monthly += monthly_pay

            html_content.append(f'''
                <tr>
                    <td>{html.escape(name)}</td>
                    <td>{data['hours']:.1f}</td>
                    <td>${data['rate']:.2f}</td>
                    <td>${weekly_pay:.2f}</td>
                    <td>${monthly_pay:.2f}</td>
                </tr>
            ''')

        html_content.append(f'''
            <tr>
                <td colspan="3"><strong>Totals</strong></td>
                <td><strong>${total_weekly:.2f}</strong></td>
                <td><strong>${total_monthly:.2f}</strong></td>
            </tr>
        ''')

        html_content.append('</table>')
        
        return ''.join(html_content)
    

class Caregiver:
    def __init__(self, name: str, phone: str, email: str, pay_rate: float = 20, hours: float = 0):
        self.validate_input(name, phone, email, pay_rate)
        self.name = name
        self.phone = phone
        self.email = email
        self.pay_rate = pay_rate
        self.hours = hours
        self.availability: Dict = {}

    @staticmethod
    def validate_input(name: str, phone: str, email: str, pay_rate: float):
        if not all([name, phone, email]):
            raise ValueError("Name, phone, and email are required!")
        if pay_rate < 0:
            raise ValueError("Pay rate cannot be negative!")
        if not email.count('@') == 1:
            raise ValueError("Email format is invalid!")

    def set_availability(self, date: str, shift: str, status: str) -> None:
        if status not in [AvailStatus.AVAILABLE, AvailStatus.UNAVAILABLE, AvailStatus.PREFERRED]:
            raise ValueError(f"Availability status is invalid! -- {status}")
        self.availability[{date, shift}] = status

    def add_hours(self, hours: float) -> None:
        if hours < 0:
            raise ValueError("Hours cannot be negative! Time doesn't flow that way!")
        self.hours += hours

### Code Below May Cause Errors -- It has been commented out ###
'''

class Schedule:
    def __init__(self, caregivers):
        #generates schedule with list of caregivers
        self.caregivers = caregivers
        self.schedule = {}  #dictionary to store the schedule
    
    def create_schedule(self, month, year):
        #generates schedule for given month and year
        import calendar
        cal = calendar.Calendar()
        for day in cal.itermonthdays(year, month):
            if day != 0:  #ignores padding days
                date = f"{year}-{month:02d}-{day:02d}"
                self.schedule[date] = {"AM": None, "PM": None}
                
        #assigns shifts based on availability and preferences 
                for shift in ["AM", "PM"]:
                        #finds all caregivers available for this date and shift
                        available_caregivers = [
                            caregiver for caregiver in self.caregivers
                            if caregiver.availability.get((date, shift), "available") != "unavailable"
                        ]

                        #prioritizes caregivers with "preferred" status
                        preferred_caregivers = [
                            caregiver for caregiver in available_caregivers
                            if caregiver.availability.get((date, shift)) == "preferred"
                        ]

                        #assigns a caregiver to the shift
                        if preferred_caregivers:
                            assigned_caregiver = preferred_caregivers[0]  # Take the first preferred
                        elif available_caregivers:
                            assigned_caregiver = available_caregivers[0]  # Take the first available
                        else:
                            assigned_caregiver = "No coverage"

                        #updates the schedule
                        self.schedule[date][shift] = assigned_caregiver.name if assigned_caregiver != "No coverage" else "No coverage"

                        #updates caregiver hours if they were assigned
                        if assigned_caregiver != "No coverage":
                            assigned_caregiver.hours += 6  # Each shift is 6 hours
                            
    def display_schedule(self):
       #displays in readable format
        print("Care Schedule:\n")
        for date, shifts in self.schedule.items():
            print(f"{date}: AM: {shifts['AM']}, PM: {shifts['PM']}")

class PayReport:
    def __init__(self, caregivers):
        #initializes pay report with list of caregivers
        self.caregivers = caregivers

    def calculate_pay(self):
        #calculates weekly and monthly pay per caregiver
        pay_data = {}
        for caregiver in self.caregivers:
            weekly_gross = caregiver.hours * caregiver.pay_rate
            pay_data[caregiver.name] = {
                "weekly_gross": weekly_gross,
                "monthly_gross": weekly_gross * 4  #simplified 
            }
        return pay_data

    def display_pay_report(self):
        #displays pay report
        print("\nPay Report:\n")
        total_weekly = 0
        total_monthly = 0
        for name, pay in self.calculate_pay().items():
            print(f"{name}: Weekly: ${pay['weekly_gross']:.2f}, Monthly: ${pay['monthly_gross']:.2f}")
            total_weekly += pay['weekly_gross']
            total_monthly += pay['monthly_gross']
        print(f"\nTotal Weekly Pay: ${total_weekly:.2f}")
        print(f"Total Monthly Pay: ${total_monthly:.2f}")

#run this, main program 
#creates caregivers
caregivers = [
    Caregiver("Alice Johnson", "545-1234", "alice@example.com"),
    Caregiver("Bob Smith", "125-5678", "bob@example.com"),
    Caregiver("Carol Lee", "355-8765", "carol@example.com"),
    Caregiver("David Brown", "555-4321", "david@example.com"),
    Caregiver("Emma Wilson", "577-6789", "emma@example.com"),
    Caregiver("Frank Green", "598-9876", "frank@example.com"),
    Caregiver("Grace White", "666-3456", "grace@example.com"),
    Caregiver("Hannah Black", "544-6543", "hannah@example.com"),
]

#sets sample availability
for caregiver in caregivers:
    for day in range(1, 8):  #example: set availability for the first week of the month
        date = f"2024-12-{day:02d}"
        caregiver.set_availability(date, "AM", "preferred" if day % 2 == 0 else "available")
        caregiver.set_availability(date, "PM", "available")

#creates the schedule
schedule = Schedule(caregivers)
schedule.create_schedule(12, 2024)  #December 2024
schedule.display_schedule()

#generates and display the pay report
pay_report = PayReport(caregivers)
pay_report.display_pay_report()
'''
