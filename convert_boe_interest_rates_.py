from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

def main():
    boe_data = read_boe("interest_rates/BOE_rates_original.csv")
    starting_date = datetime(2010, 12,1)
    end_date = datetime(2025,6,30)
    monthly_accumulations = obtain_monthly_cash_accrual(boe_data, starting_date, end_date)
    write_interest_rates('gbp_monthly_returns/Moneymarket_monthly_returns_GBP.csv', monthly_accumulations)
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
    if not interest_rate_data:
        return [] # Handle empty interest rate data

    monthly_accumulations = []
    
    # 1. Determine the initial current_rate_index
    # Find the latest rate change ON or BEFORE the starting_date.
    # Since interest_rate_data is DESCENDING, we iterate and take the first one found.
    current_rate_index = len(interest_rate_data) - 1 # Default to the oldest rate if starting_date is earlier than all
    for i, entry in enumerate(interest_rate_data):
        if entry.date <= starting_date:
            current_rate_index = i
            break
    # After this loop, interest_rate_data[current_rate_index] is the rate active at starting_date.

    # 2. Set up the monthly iteration
    # Start calculations from the beginning of the month of starting_date, but not before starting_date itself.
    current_month_first_day = datetime(starting_date.year, starting_date.month, 1)
    
    # Loop month by month
    # We want to go until the month that contains end_date
    while current_month_first_day <= end_date:
        monthly_accumulation_factor = 1.0 # Reset for each new month

        # Determine the actual start day for daily accrual in this month
        # It's either the starting_date itself (for the first month) or the 1st of the current month
        day_for_daily_accrual_start = max(current_month_first_day, starting_date)

        # Determine the actual end day for daily accrual in this month
        # This is the last day of the current_month_first_day, but not exceeding end_date.
        next_month_first_day = current_month_first_day + relativedelta(months=1)
        day_for_daily_accrual_end = min(next_month_first_day - relativedelta(days=1), end_date)

        current_day_in_loop = day_for_daily_accrual_start

        # Loop day by day within the effective period of the current month
        while current_day_in_loop <= day_for_daily_accrual_end:
            # Update current_rate_index if a *newer* rate has become active on or before current_day_in_loop.
            # We are moving BACKWARDS (towards index 0) in the list as dates get newer.
            while current_rate_index > 0 and \
                  interest_rate_data[current_rate_index - 1].date <= current_day_in_loop:
                current_rate_index -= 1
            
            current_interest_rate_entry = interest_rate_data[current_rate_index]
            annual_rate = current_interest_rate_entry.annual_rate
            
            # Apply daily accrual, handling leap years
            days_in_year = 366 if calendar.isleap(current_day_in_loop.year) else 365
            monthly_accumulation_factor *= (1 + (annual_rate / 100))**(1/days_in_year)
            
            current_day_in_loop += relativedelta(days=1)
        
        # Store the monthly accumulation if we processed any days in this month
        # The date for the entry should be the last day for which accumulation was done in this month.
        if day_for_daily_accrual_start <= day_for_daily_accrual_end: # Check if any days were processed
            # The date associated with the monthly accumulation should be the last day of the period
            # this accumulation covers within that month.
            accumulation_end_date = day_for_daily_accrual_end # This makes sense for a monthly "total"
            monthly_accumulations.append(BOEInterestRate(accumulation_end_date, monthly_accumulation_factor))
        
        # Move to the next calendar month for the outer loop
        current_month_first_day = next_month_first_day

    return monthly_accumulations

def first_day_of_next_month(dt=None):
    if dt is None:
        dt = datetime.now()
    year = dt.year + (dt.month == 12)
    month = 1 if dt.month == 12 else dt.month + 1
    return datetime(year, month, 1)

def write_interest_rates(filepath, monthly_accumulations):
    with open(filepath, 'w') as new_file:
        new_file.write("Date,Monthly_Return\n")
        for entry in monthly_accumulations:
            date_string = entry.date.strftime('%Y-%m-%d')
            monthly_accumulation = entry.annual_rate -1
            entry_string = f"{date_string},{monthly_accumulation}\n"
            new_file.write(entry_string)

main()