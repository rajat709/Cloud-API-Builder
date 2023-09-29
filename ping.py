import requests
import time

# Define the URL to visit
url = "your_url"

# Function to visit the site and check status
def visit_site():
    while True:
        try:
            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the status code indicates success (e.g., 200 OK)
            if response.status_code == 200:
                print("Successful visit at", time.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                print("Unsuccessful visit at", time.strftime("%Y-%m-%d %H:%M:%S"))

            # Sleep for 30 seconds to stay on the site
            time.sleep(30)

        except Exception as e:
            print("Error:", str(e))

        # Sleep for 6 hours before the next visit
        time.sleep(6 * 60 * 60)

if __name__ == "__main__":
    # Start visiting the site
    visit_site()
