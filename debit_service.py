import calendar

from datetime import timedelta, datetime

from dateutil import parser, utils

# Map text input to calendar days
# Only business days (Monday-Friday) are valid
from exceptions import ValidationError

DAY_OF_WEEK = {
    "monday": calendar.MONDAY,
    "tuesday": calendar.TUESDAY,
    "wednesday": calendar.WEDNESDAY,
    "thursday": calendar.THURSDAY,
    "friday": calendar.FRIDAY
}

# In a prod app this would be ideally be read in from a web service so it isn't static
FED_RESERVE_HOLIDAYS_2022 = (
    datetime(2022, 1, 1),
    datetime(2022, 1, 17),
    datetime(2022, 2, 21),
    datetime(2022, 5, 30),
    datetime(2022, 6, 19),
    datetime(2022, 7, 4),
    datetime(2022, 9, 5),
    datetime(2022, 10, 10),
    datetime(2022, 11, 11),
    datetime(2022, 11, 24),
    datetime(2022, 12, 25),
)


class DebitService:

    def __init__(self, loan_request):
        self.monthly_payment_amount = loan_request['monthly_payment_amount']
        self.payment_due_date = loan_request['payment_due_day']
        self.schedule_type = loan_request['schedule_type']
        self.debit_start_date = parser.parse(loan_request['debit_start_date'])
        # Example validation function. I would extend to request variables, checking negative values etc.
        self.debit_day_of_week = self.validate_day_of_week(loan_request['debit_day_of_week'])

    def calculate_next_payment(self):
        today = utils.today()
        start_date = self.debit_start_date
        date = start_date
        date, amount = self.__calculate_next_debit_date(date, today)

        return {"debit": {"amount": amount, "date": date.strftime("%Y-%m-%d")}}

    def __calculate_next_debit_date(self, date, today):
        if self.schedule_type == 'biweekly':
            day_step = 14
        # extend here if adding other debit frequencies
        else:
            day_step = 14
        # extend here if adding other debit frequencies
        while date <= today:
            date += timedelta(days=day_step)
        amount = self.__calculate_next_debit_amount(date)
        # Apply rationale to handle fed holidays
        if date in FED_RESERVE_HOLIDAYS_2022 and date.weekday() != 5:
            date = date + timedelta(days=1)
        return date, amount

    def __calculate_next_debit_amount(self, date):
        num_days_in_month = calendar.monthcalendar(date.year, date.month)
        num_days = sum(1 for x in num_days_in_month if x[self.debit_day_of_week] != 0)
        if num_days > 4:
            return self.monthly_payment_amount / 3
        else:
            return self.monthly_payment_amount / 2

    @staticmethod
    def validate_day_of_week(day_of_week):
        try:
            debit_day_of_week = DAY_OF_WEEK[day_of_week]
        except KeyError as err:
            raise ValidationError("Invalid debit day provided, valid days are Mon-Fri") from err
        return debit_day_of_week
