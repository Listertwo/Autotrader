import pandas as pd
import datetime

from utils.logger import logger
from config import REQUIRED_COLUMNS

#REQUIRED_COLUMNS = {"Open", "Close", "High", "Low", "Volume"}
DATE_COLUMNS = {"Date", "Datetime", "Timestamp", "Time"}

def normalize_dataframe(df: pd.dataframe) -> pd.dataframe:
    """
    
    returns
    --------
    dataframe
    """

    #Validation of dataframe
    if not isinstance(df, pd.dataframe):
        raise TypeError("Expected a pandas DataFrame")
    if df.empty:
        raise ValueError("Cannot normalize an empty dataframe")
    
    #Creates copy of df for normalization
    df = df.copy()
    
    #Define column labels
    colcount = REQUIRED_COLUMNS - set(df.columns)
    
    if len(colcount) > 0:
        raise ValueError(f"missing required columns: {sorted(colcount)}")
    if len(colcount) < 0:
        logger.info(f"dataframe has extra columns: {sorted(colcount)}")
    
    #Normallizes index as a datetime
    if not isinstance(df.index, pd.DatetimeIndex): #Is the Index not a Datetime?
        found = False
        for column in DATE_COLUMNS: #Look for common column names
            if column in df.columns: #Is a possible column name in the dataframe?
                colConvert = pd.to_datetime(df[column], errors='coerce') #Try to convert the column to a Datetime
                if colConvert.notna().all(): #Did the column not return NaT?
                    df[column] = colConvert #Sync the column with the converted version
                    df.set_index(column, inplace=True) #Set the column as the new index
                    df.sort_index(inplace=True)
                    df.index_name = "Date"
                    found = True
                    break #Found an index, no need to loop anymore!
            else:
                df.set_index(column, inplace=True) #Set the column as the new index
                found = True
                break #Found an index, no need to loop anymore!
        if not found: #Does the loop end without a new index?
            if isinstance(df.index, pd.RangeIndex): #Is the current index specifically a range?
                logger.error("Dataframe contains no datetime information.")
                raise ValueError("Dataframe contains no datetime information.")
            else: #The Index is not a Datetime and is not a Range
                df.index = pd.to_datetime(df.index, errors='coerce') #Try to convert the index to a Datetime
                    if df.index.isna().all(): #Did the index return NaT?
                        logger.error("Dataframe contains no datetime information.")
                        raise ValueError("Dataframe contains no datetime information.")
                
            
    #Sorts the index
    df.sort_index(inplace=True)
    
    #Removes duplicate entries
    df = df[~df.index.duplicated(keep="last")]
    
    #Normalizes data in columns as numeric
    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    
    #Deletes rows that have NaN
    df.dropna(subset=["Open", "High", "Low", "Close"], inplace=True)
    df["Volume"] = df["Volume"].fillna(0)

    #Price validation
    if (df[["Open", "High", "Low", "Close"]] < 0).any().any():
        raise ValueError("Negitive prices aren't allowed.")

    if (df["High"] < df["Low"]).any():
        raise ValueError("High cannot be greater than Low.")

    if (df["Open"] > df["High"]).any():
        raise ValueError("The OPENING price cannot be GREATER THAN the HIGHEST price of the day.")

    if (df["Open"] < df["Low"]).any():
        raise ValueError("The OPENING price cannot be LESS THAN the LOWEST price of the day.")

    if (df["Close"] > df["High"]).any():
        raise ValueError("The CLOSING price cannot be GREATER THAN the HIGHEST price of the day.")

    if (df["Close"] < df["Low"]).any():
        raise ValueError("The CLOSING price cannot be LESS THAN the LOWEST price of the day.")

    return df
