import asyncio
import asyncio
import speedtest
import socket
import datetime
from tqdm import tqdm
import aiohttp

def get_local_ip():
    try:
        # Create a socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return "N/A"

def is_peak_hour():
    now = datetime.datetime.now()
    hour = now.hour
    return 8 <= hour < 18  # Adjust peak hours based on your definition

async def run_speed_test(test_num, st):
    async def download_progress(session, url):
        async with session.get(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            progress_bar = tqdm(total=total_size, desc=f"Test #{test_num}", unit="B", unit_scale=True)

            async for chunk in response.content.iter_any():
                progress_bar.update(len(chunk))

            progress_bar.close()

    url = "http://ipv4.download.thinkbroadband.com/10MB.zip"  # Using a sample download URL
    async with aiohttp.ClientSession() as session:
        await download_progress(session, url)

    upload_speed = await asyncio.to_thread(st.upload) / 10**6  # in Mbps
    download_speed = await asyncio.to_thread(st.download) / 10**6  # in Mbps

    return upload_speed, download_speed

async def speed_test():
    local_ip = get_local_ip()
    print(f"Local IP Address: {local_ip}")

    now = datetime.datetime.now()
    print(f"Current Date and Time: {now}")

    if is_peak_hour():
        print("Current hour is peak hour.")
    else:
        print("Current hour is off-peak hour.")

    st = speedtest.Speedtest()

    upload_speeds = []
    download_speeds = []

    num_tests = 5

    with open("data.txt", "a") as file:
        file.write(f"\n\nDate: {now}\n")
        file.write(f"Local IP Address: {local_ip}\n")
        if is_peak_hour():
            file.write("Current hour is peak hour.\n")
        else:
            file.write("Current hour is off-peak hour.\n")

    for test_num in range(1, num_tests + 1):
        print(f"\nRunning Speed Test #{test_num}")

        upload_speed, download_speed = await run_speed_test(test_num, st)

        upload_speeds.append(upload_speed)
        download_speeds.append(download_speed)

        with open("data.txt", "a") as file:
            file.write(f"\nTest #{test_num} - Upload Speed: {upload_speed:.2f} Mbps\n")
            file.write(f"Test #{test_num} - Download Speed: {download_speed:.2f} Mbps\n")

    average_upload = sum(upload_speeds) / num_tests
    average_download = sum(download_speeds) / num_tests

    with open("data.txt", "a") as file:
        file.write(f"\nAverage Upload Speed: {average_upload:.2f} Mbps\n")
        file.write(f"Average Download Speed: {average_download:.2f} Mbps\n")

    # Print the data
    print("\nUpload Speeds:")
    for test_num, speed in enumerate(upload_speeds, start=1):
        print(f"Test #{test_num} - Upload Speed: {speed:.2f} Mbps")

    print("\nDownload Speeds:")
    for test_num, speed in enumerate(download_speeds, start=1):
        print(f"Test #{test_num} - Download Speed: {speed:.2f} Mbps")

    print(f"\nAverage Upload Speed: {average_upload:.2f} Mbps")
    print(f"Average Download Speed: {average_download:.2f} Mbps")

if __name__ == "__main__":
    asyncio.run(speed_test())
