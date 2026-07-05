from utils.validator import validate_normalize 
from datetime import datetime

validate_normalize("AAPL", None, None, "1y", "1d")

#validate_normalize(123, None, None, "1y", "1d") #symbol validation
validate_normalize("appl", None, None, "1y", "1d") #symbol normalization
#validate_normalize("AAPL", None, None, "bananna", "1d") #period validation
validate_normalize("AAPL", None, None, "1Y", "1d") #period normalization
#validate_normalize("AAPL", None, None, "1y", "bananna") #interval validation
validate_normalize("AAPL", None, None, "1y", "1D") #interval normalization
#validate_normalize("AAPL", 123, None, "1y", "1d") #start date validation
#validate_normalize("AAPL", None, 123, "1y", "1d") #end date validation
#validate_normalize("AAPL", datetime(2026, 1, 1), datetime(2025, 1, 1), "1y", "1d") #start date before end date validation