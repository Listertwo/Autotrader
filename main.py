from data.downloader import download_data

df = download_data("AAPL", period="5y")

print(df.head())