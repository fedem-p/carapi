import requests
import os


def update_autoscout_sample_html():
    """
    Downloads the latest HTML from AutoScout24 search page and overwrites autoscout_sample.html.
    """
    print("starting update_autoscout_sample_html")
    url = "https://www.autoscout24.com/lst/search?atype=C&body=2%2C3%2C4%2C5%2C6&custtype=D&cy=D&desc=0&emclass=&ensticker=&eq=&fregfrom=2020&kmto=100000&powerfrom=86&powertype=hp&fuel=2%2C3%2CB%2CD&page=1&priceto=20000&seatsfrom=4&sort=standard&damaged_listing=exclude&ocs_listing=include&ustate=N%2CU"
    response = requests.get(url)
    response.raise_for_status()
    sample_path = os.path.join(os.path.dirname(__file__), "autoscout_sample.html")
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"Updated {sample_path} with latest HTML from {url}")


if __name__ == "__main__":
    update_autoscout_sample_html()
