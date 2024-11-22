
# Project Code (version 1.0)

import calendar

class Caregiver:
    def __init__(self, name, phone, email, pay_rate=20, hours=0):
        #initialize caregiver with information needed
        self.name = name
        self.phone = phone
        self.email = email
        self.pay_rate = pay_rate
        self.hours = hours
        self.availability = {}  #dictionary with date and shift preferences

    def set_availability(self, date, shift, status):
        #updates availability per caregiver
        self.availability[(date, shift)] = status

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

