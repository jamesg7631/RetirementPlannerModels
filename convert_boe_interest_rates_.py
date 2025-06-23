from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

def main():
    boe_data = read_boe("interest_rates/BOE_rates_original.csv")
    starting_date = datetime(2010, 11,1)
    end_date = datetime(2025,6,21)
    monthly_acculations = obtain_monthly_cash_accrual(boe_data, starting_date, end_date)
    print()
      

class BOEInterestRate:

    def __init__(self, date, annual_rate):
        self.date = date
        self.annual_rate = annual_rate

def read_boe(filepath):
        interest_rates = []
        with open(filepath) as new_file:
            next(new_file)
            for line in new_file:
                items = line.split(',')
                original_date = items[0]
                date_obj = datetime.strptime(original_date, "%d %b %y")
                interest_rate_entry = BOEInterestRate(date_obj, float(items[1]))
                interest_rates.append(interest_rate_entry)

        return interest_rates

def obtain_monthly_cash_accrual(interest_rate_data: list, starting_date, end_date):
    current_list_index = 0
    month_starting_date = datetime(year=starting_date.year, month = starting_date.month, day=1)

    for i, entry in enumerate(interest_rate_data):
        if entry.date <= starting_date:
            current_rate_index = i
            break

    next_month = month_starting_date + relativedelta(months=1)

    # Find monthly accumulation
    monthly_accumulations = []
    current_day = month_starting_date
    current_interest_rate_entry = interest_rate_data[current_list_index]
    boe_interest_rate_change_entry = interest_rate_data[current_list_index - 1]
    monthly_accumulation = 1
    final_month = first_day_of_next_month(datetime.now())
    while current_day < final_month:
        while current_day < next_month:
            boe_interest_rate_change_date = boe_interest_rate_change_entry.date
            if current_day >= boe_interest_rate_change_date or boe_interest_rate_change_date == None:
                current_list_index = current_list_index -1
                #If the below is reached, we have no further changes in Bank of England interest rates
                if current_list_index < 0:
                    break
                current_interest_rate_entry = interest_rate_data[current_list_index]
            days_in_year = 366 if calendar.isleap(current_day.year) else 365
            monthly_accumulation *= (1 + (current_interest_rate_entry.annual_rate / 100))**(1/days_in_year)
            current_day = current_day + relativedelta(days=1)
        final_date_in_month = next_month - relativedelta(days=1)
        next_month = next_month + relativedelta(months=1)
        monthly_accumulation_entry = BOEInterestRate(final_date_in_month, monthly_accumulation)
        monthly_accumulations.append(monthly_accumulation_entry)

    return monthly_accumulations

def first_day_of_next_month(dt=None):
    if dt is None:
        dt = datetime.now()
    year = dt.year + (dt.month == 12)
    month = 1 if dt.month == 12 else dt.month + 1
    return datetime(year, month, 1)



    

    



main()