
# Project Code (version 1.1)
# The purpose of this program is to create a schedule for caregivers. 
# The program takes into account every persons’ availability and accommodates it towards the patient's schedule.

from abc import ABC, abstractmethod
from datetime import datetime
import calendar
import html
import os
from typing import Dict, List, Optional


class AvailStatus:
    PREFERRED = 'preferred'
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'

class ScheduleFormatter(ABC):
    @abstractmethod
    def format_schedule(self, schedule: Dict, month: int, year: int) -> str:
        pass

#Create calendar for the schedule
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
        
# Create a pay report to pay caretakers 
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
    
#Create profile for caregiver allowing input for avaliability to work
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
        self.availability[(date, shift)] = status

    def get_availability(self, date: str, shift: str) -> None:
        return self.availability.get((date, shift), AvailStatus.AVAILABLE)

    def add_hours(self, hours: float) -> None:
        if hours < 0:
            raise ValueError("Hours cannot be negative! Time doesn't flow that way!")
        self.hours += hours
# Create schedule to allow for everything to be taken into account and viewable
class Schedule:
    def __init__(self, caregivers: List[Caregiver]):
        self.caregiver = caregivers
        self.schedule: Dict = {}
        self.formatter = HTMLScheduleFormatter()

    def create_schedule(self, month: int, year: int) -> None:
        self._validate_date(month, year)
        cal = calendar.Calendar()

        for day in cal.itermonthdays(year, month):
            if day != 0:
                self._schedule_day(day, month, year)

    def _validate_date(self, month: int, year: int) -> None:
        if not 1 <= month <= 12:
            raise ValueError("Invalid month!")
        if year < 2000:
            raise ValueError("Invalid year!")
        
    def _schedule_day(self, day: int, month: int, year: int) -> None:
        date = f'{year}-{month:02d}-{day:02d}'
        self.schedule[date] = {"AM": None, "PM": None}

        for shift in ['AM', 'PM']:
            self._assign_shift(date, shift)

    def _assign_shift(self, date: str, shift: str) -> None:
        available_caregivers = [
            caregiver for caregiver in self.caregiver
            if caregiver.get_availability(date, shift) != AvailStatus.UNAVAILABLE
        ]
        preferred_caregivers = [
            caregiver for caregiver in self.caregiver
            if caregiver.get_availability(date, shift) == AvailStatus.PREFERRED
        ]

        if preferred_caregivers:
            assigned_caregiver = min(preferred_caregivers, key=lambda x: x.hours)
        elif available_caregivers:
            assigned_caregiver = min(available_caregivers, key=lambda x: x.hours)
        else:
            assigned_caregiver = None

        if assigned_caregiver:
            assigned_caregiver.add_hours(6)
            self.schedule[date][shift] = assigned_caregiver.name
        else:
            self.schedule[date][shift] = "No coverage"

    def display_schedule(self) -> None:
        print("Care Schedule:\n")
        for date, shifts in self.schedule.items():
            print(f"{date}: AM: {shifts['AM']}, PM: {shifts['PM']}")

    def generate_html_schedule(self, month: int, year: int) -> str:
        return self.formatter.format_schedule(self.schedule, month, year)
    
class PayReport:
    def __init__(self, caregivers: List[Caregiver]):
        self.caregivers = caregivers

    def calculate_pay(self) -> Dict:
        pay_data = {}
        for caregiver in self.caregivers:
            weekly_gross = caregiver.hours * caregiver.pay_rate
            pay_data[caregiver.name] = {
                "hours": caregiver.hours,
                "rate": caregiver.pay_rate,
                "weekly_gross": weekly_gross,
                "monthly_gross": weekly_gross * 4
            }
        return pay_data
    
    def generate_html_report(self) -> str:
        pay_data = self.calculate_pay()
        total_weekly = sum(data["weekly_gross"] for data in pay_data.values())
        total_monthly = sum(data["monthly_gross"] for data in pay_data.values())

        html_content = [
            '''
            <div class="pay-report">
                <h2>Pay Report</h2>
                <table border="1">
                    <thread>
                        <tr>
                            <th>Caregiver</th>
                            <th>Hours</th>
                            <th>Rate</th>
                            <th>Weekly Pay</th>
                            <th>Monthly Pay</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
        ]

        for name, data in pay_data.items():
            row = f'''
                <tr>
                    <td>{html.escape(name)}</td>
                    <td>{data["hours"]:.1f}</td>
                    <td>${data["rate"]:.2f}</td>
                    <td>${data["weekly_gross"]:.2f}</td>
                    <td>${data["monthly_gross"]:.2f}</td>
                </tr>
            '''
            html_content.append(row)

        html_content.append(f'''
                    <tr class="totals-row">
                        <th colspan="3">Totals:</th>
                        <td>${total_weekly:.2f}</td>
                        <td>${total_monthly:.2f}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        ''')

        return '\n'.join(html_content)
    
    def display_pay_report(self) -> None:
        pay_data = self.calculate_pay()
        print("\nPay report:\n")
        total_weekly = 0
        total_monthly = 0

        for name, pay in pay_data.items():
            print(f"{name}:")
            print(f"  Hours: {pay['hours']:.1f}")
            print(f"  Rate: ${pay['rate']:.2f}")
            print(f"  Weekly Pay: ${pay['weekly_gross']:.2f}")
            print(f"  Monthly Pay: ${pay['monthly_gross']:.2f}\n")
            total_weekly += pay['weekly_gross']
            total_monthly += pay['monthly_gross']

        print(f"Total Weekly Pay: ${total_weekly:.2f}")
        print(f"Total Monthly Pay: ${total_monthly:.2f}")

if __name__ == "__main__":
    caregivers = [
        Caregiver("Mahad Khan", "301-1234", "mkhan@testcase.com"),
        Caregiver("Derek d'Agostino", "301-5678", "dagostino@testcase.com"),
        Caregiver("Brendan Dorrian", "301-8901", "bdorrian@testcase.com"),
    ]


    caregivers[0].pay_rate = 25.0
    caregivers[1].pay_rate = 30.0
    caregivers[2].pay_rate = 28.0

    for caregiver in caregivers:
        caregiver.add_hours(40)  
        for day in range(1, 8):
            date = f"2024-12-{day:02d}"
            caregiver.set_availability(
                date,
                "AM",
                AvailStatus.PREFERRED if day % 2 == 0 else AvailStatus.AVAILABLE
            )
            caregiver.set_availability(date, "PM", AvailStatus.AVAILABLE)


    caregivers[0].set_availability("2024-12-25", "AM", AvailStatus.UNAVAILABLE)
    caregivers[0].set_availability("2024-12-25", "PM", AvailStatus.UNAVAILABLE)


    schedule = Schedule(caregivers)
    schedule.create_schedule(12, 2024)
    print("\nDisplaying full schedule:")
    schedule.display_schedule()


    html_schedule = schedule.generate_html_schedule(12, 2024)
    print("\nHTML Schedule generated successfully")


    pay_report = PayReport(caregivers)
    print("\nDisplaying pay report:")
    pay_report.display_pay_report()

    html_pay_report = pay_report.generate_html_report()
    print("\nHTML Pay Report generated successfully")


html_path = "schedule.html"
pay_path = "pay_report.html"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_schedule)
print(f"Schedule saved to: {os.path.abspath(html_path)}")

with open(pay_path, "w", encoding="utf-8") as f:
    f.write(html_pay_report)
print(f"Pay report saved to: {os.path.abspath(pay_path)}")
