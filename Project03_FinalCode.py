
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
    '''
    A class containing const(s) for caregiver availability status.
    '''
    PREFERRED = 'preferred'
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'

class ScheduleFormatter(ABC):
    '''
    A abstract base class defining the interface for schedule formatting.
    '''
    @abstractmethod
    def format_schedule(self, schedule: Dict, month: int, year: int) -> str:
        pass


class HTMLScheduleFormatter(ScheduleFormatter):
    '''
    A class implementation for a formatter that generates HTML formatted schedules.
    '''
    def format_schedule(self, schedule: Dict, month: int, year: int) -> str:
        '''
        Creates a calendar format for the schedule.

        Args:
            schedule (Dict): A dictionary mapping dates for shift coverage.
            month (int): The month to be displayed.
            year (int): The year to be displayed.

        Returns:
            str: A HTML string containing the formatted calendar with shift information & more.
        '''
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
        '''
        Formats the pay report, responsible for paying caretakers. 

        Args:
            pay_data (Dict): A dictionary mapping caretaker names to their payment info.

        Returns:
            str: A HTML string containing a formatted payment report table including:
                - Caretaker names
                - Hours worked
                - Hourly rates
                - Weekly pay calculations
                - Monthly pay calculations
                - Total payments
        '''
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
    '''
    A class to repersent caregivers with their personal information as well as availability.
    '''
    def __init__(self, name: str, phone: str, email: str, pay_rate: float = 20, hours: float = 0):
        '''
        Initializes a new Caregiver instance.

        Args:
            name (str): Name of caretaker.
            phone (str): Phone number of caretaker.
            email (str): Email of caretaker.
            pay_rate (float): Caretaker hourly pay rate. Defaults to 20.
            hours (float): Caretaker hours worked. Defaults to 0.

        Raises:
            ValueError: If fields left empty, pay rate is negative, or email format is invalid. 
        '''
        self.validate_input(name, phone, email, pay_rate)
        self.name = name
        self.phone = phone
        self.email = email
        self.pay_rate = pay_rate
        self.hours = hours
        self.availability: Dict = {}

    @staticmethod
    def validate_input(name: str, phone: str, email: str, pay_rate: float):
        '''
        Validate the input parameters for a caregiver.

        Args:
            name (str): Name of caretaker.
            phone (str): Phone number of caretaker.
            email (str): Email of caretaker.
            pay_rate (float): Caretaker hourly pay rate.

        Raises:
            ValueError: If fields left empty, pay rate is negative, or email format is invalid. 
        '''
        if not all([name, phone, email]):
            raise ValueError("Name, phone, and email are required!")
        if pay_rate < 0:
            raise ValueError("Pay rate cannot be negative!")
        if not email.count('@') == 1:
            raise ValueError("Email format is invalid!")

    def set_availability(self, date: str, shift: str, status: str) -> None:
        '''
        Set the availability of a caregiver for a specific date and shift.

        Args:
            date (str): The date in string format.
            shift (str): The shift identifier -- either AM or PM.
            status (str): Availability status from AvailStatus Class.

        Raises:
            ValueError: If the availability status is not a valid AvailStatus value.
        '''
        if status not in [AvailStatus.AVAILABLE, AvailStatus.UNAVAILABLE, AvailStatus.PREFERRED]:
            raise ValueError(f"Availability status is invalid! -- {status}")
        self.availability[(date, shift)] = status

    def get_availability(self, date: str, shift: str) -> None:
        '''
        Get the availability status for a specific date and shift.

        Args:
            date (str): The date to check.
            shift (str): The shift to check -- either AM or PM.

        Returns:
            str: The availability status (defaulting to Available if not set).
        '''
        return self.availability.get((date, shift), AvailStatus.AVAILABLE)

    def add_hours(self, hours: float) -> None:
        '''
        Add worked hours to the caregivers total.

        Args:
            hours (float): Number of hours to be added.

        Raises:
            ValueError: If hours is a negative number.
        '''
        if hours < 0:
            raise ValueError("Hours cannot be negative! Time doesn't flow that way!")
        self.hours += hours

class Schedule:
    '''
    A class to create the schedule among other functions.
    '''
    def __init__(self, caregivers: List[Caregiver]):
        '''
        Initializes a new Schedule instance.

        Args:
            caregivers (List[Caregiver]): A list of caregivers available for scheduling.
        '''
        self.caregiver = caregivers
        self.schedule: Dict = {}
        self.formatter = HTMLScheduleFormatter()

    def create_schedule(self, month: int, year: int) -> None:
        '''
        Creates a complete schedule for the given month and year -- considers caregiver availability and workload balance.

        Args:
            month (int): Month to be scheduled.
            year (int): Year to be scheduled.

        Raises:
            ValueError: If a month or year is invalid. 
        '''
        self._validate_date(month, year)
        cal = calendar.Calendar()

        for day in cal.itermonthdays(year, month):
            if day != 0:
                self._schedule_day(day, month, year)

    def _validate_date(self, month: int, year: int) -> None:
        '''
        Validate the given month and year.

        Args:
            month (int): Month to be validated.
            year (int): Year to be validated.

        Raises:
            ValueError: If month is not 1-12 OR if year is before 2000.
        '''
        if not 1 <= month <= 12:
            raise ValueError("Invalid month!")
        if year < 2000:
            raise ValueError("Invalid year!")
        
    def _schedule_day(self, day: int, month: int, year: int) -> None:
        '''
        Schedule both AM and PM shifts for a particular day.

        Args:
            day (int): Day of month.
            month (int): Month, ranging from 1-12.
            year (int): Put simply, the year.
        '''
        date = f'{year}-{month:02d}-{day:02d}'
        self.schedule[date] = {"AM": None, "PM": None}

        for shift in ['AM', 'PM']:
            self._assign_shift(date, shift)

    def _assign_shift(self, date: str, shift: str) -> None:
        '''
        Assigns a caregiver to a specific shift, based on factors such as:
            - Preference
            - General availability
            - Current workload
        Marks no coverage, if and only if, none is available.

        Args:
            date (str): Date -- in YYYY-MM-DD format.
            shift (str): Shift to assign -- either AM or PM.
        '''
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
        '''
        Displays the schedule in a simple, text format, and prints each date with its AM and PM shift assignements.
        '''
        print("Care Schedule:\n")
        for date, shifts in self.schedule.items():
            print(f"{date}: AM: {shifts['AM']}, PM: {shifts['PM']}")

    def generate_html_schedule(self, month: int, year: int) -> str:
        '''
        Generates a HTML formatter version of the schedule.

        Args:
            month (int): Month to be display.
            year (int): Year to be display.

        Returns:
            str: HTML formatted schedule. 
        '''
        return self.formatter.format_schedule(self.schedule, month, year)
    
class PayReport:
    """
    A class to generate and display pay reports for caregivers.
    """
    def __init__(self, caregivers: List[Caregiver]):
        '''
        Initializes a new PayReport instance.

        Args:
            caregivers (List[Caregiver]): A list of caregivers to generate reports for.
        '''
        self.caregivers = caregivers

    def calculate_pay(self) -> Dict:
        """
        Calculates payment details for all caregivers.
        
        Returns:
            Dict: a dictionary where keys are caregiver names, values are dictionaries containing hours, payrate, etc.
        """
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
        """
        Generates a HTML formatted pay report.

        Returns:
            str: HTML formatted string, which contains:
                - A table with caregiver payment details
                - Hours worked
                - Pay rates
                - Weekly and monthly pay calculations
                - Total payments across all caregivers
        """
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

        #adds rows for each caregivers details
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

        #adds totals row
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
        """
        Displays the pay report to console/CLI.
        """
        pay_data = self.calculate_pay()
        print("\nPay report:\n")
        total_weekly = 0
        total_monthly = 0

        #prints pay details for caregivers
        for name, pay in pay_data.items():
            print(f"{name}:")
            print(f"  Hours: {pay['hours']:.1f}")
            print(f"  Rate: ${pay['rate']:.2f}")
            print(f"  Weekly Pay: ${pay['weekly_gross']:.2f}")
            print(f"  Monthly Pay: ${pay['monthly_gross']:.2f}\n")
            total_weekly += pay['weekly_gross']
            total_monthly += pay['monthly_gross']

        #prints out totals
        print(f"Total Weekly Pay: ${total_weekly:.2f}")
        print(f"Total Monthly Pay: ${total_monthly:.2f}")

if __name__ == "__main__":
    caregivers = [
        Caregiver("Mahad Khan", "301-1234", "mkhan@testcase.com"),
        Caregiver("Derek d'Agostino", "301-5678", "dagostino@testcase.com"),
        Caregiver("Brendan Dorrian", "301-8901", "bdorrian@testcase.com"),
    ]

    #sets pay rates and hours
    caregivers[0].pay_rate = 25.0
    caregivers[1].pay_rate = 30.0
    caregivers[2].pay_rate = 28.0

    for caregiver in caregivers:
        caregiver.add_hours(40)  
        for day in range(1, 8):    #sets availability for week
            date = f"2024-12-{day:02d}"
            caregiver.set_availability(
                date,
                "AM",
                AvailStatus.PREFERRED if day % 2 == 0 else AvailStatus.AVAILABLE
            )
            caregiver.set_availability(date, "PM", AvailStatus.AVAILABLE)

    #marks availability for christmas holiday
    caregivers[0].set_availability("2024-12-25", "AM", AvailStatus.UNAVAILABLE)
    caregivers[0].set_availability("2024-12-25", "PM", AvailStatus.UNAVAILABLE)

    #generate a display schedule
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

#saves reports to files
html_path = "schedule.html"
pay_path = "pay_report.html"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_schedule)
print(f"Schedule saved to: {os.path.abspath(html_path)}")

with open(pay_path, "w", encoding="utf-8") as f:
    f.write(html_pay_report)
print(f"Pay report saved to: {os.path.abspath(pay_path)}")
