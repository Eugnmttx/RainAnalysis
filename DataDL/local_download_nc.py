import requests

url = "https://psl.noaa.gov/thredds/fileServer/Datasets/COBE2/sst.mon.mean.nc"

print("Downloading file...")
response = requests.get(url, stream=True)

# Check if the request was successful
if response.status_code == 200:
    with open("sst.mon.mean.nc", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("✅ Download complete: sst.mon.mean.nc")
else:
    print(f"❌ Download failed: {response.status_code} - {response.reason}")
