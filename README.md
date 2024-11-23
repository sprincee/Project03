# Project03

Project03 -- A scheduling program done for INST326 during Fall 2024. 

Requirements:
  Care is required 12 hours per day, 7 days a week. There are two shifts each day: 7:00 AM - 1:00 PM, and 1:00 PM to 7:00 PM. There are a total of 8 caregivers. Some are family members and some are paid. Each caregiver has their own availability for shifts that is generally the same from month to month, but there are exceptions for work, vacations, and other      responsibilities. Your program should do the following:
    - Manage caregivers and their schedules. Attributes include: name, phone, email, pay rate, and hours.
    - Each caregiver should have their own availability schedule where they can indicate their availability for each shift. Availability categories are 'preferred', 'available' (default), and 'unavailable'.
    - Create a care schedule that covers AM and PM shifts and displays caregiver names on a calendar (see example). The schedule should accomodate caregivers' individual schedules and availability preferences. The python calendar module provides options for creating HTML calendars. Sample code for the HTML calendar is in the project folder.
    - Paid caregivers are paid weekly at $20/hr. Your program should calculate weekly pay based on assigned hours. Provide a separate pay report that lists weekly (gross: hours x rate) amounts to each caregiver, along with weekly and monthly totals. The report can be a text document, or presented in GUI or HTML format.

Group Requirements:
  - Your submitted project should follow OOP principles like abstraction, encapsulation, inheritance, and polymorphism as appropriate. Your program should use classes.
  - Select a group leader who will host the group's project repository on their GitHub.
  - Create the group repository and add a main program document. See example.
  - Create branches off the main program for each group member, and assign part of the program to each member.
  - Each member should work on their branch.
  - When each member is finished, merge the branches back into the main program. You may use 'merge' or 'pull requests', your choice.
  - Iterate and debug as necessary.

Deliverables:
  - Include your group number and the names of all group members in the signature block at the top of this notebook.
  - In the cell below, paste the link to your project repository. One link per group. The grader will review the activity and history provided by GitHub. To add a hyperlink to a Jupyter markdown cell, follow the instructions in the cell below.
  - Below the GitHub Repository Link cell is a code cell. Copy and paste your final program code into this cell.
