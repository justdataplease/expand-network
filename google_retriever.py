from playwright.sync_api import sync_playwright
import urllib.parse
import time
import pandas as pd

# Main query
QUERY = 'site:gr.linkedin.com/in/ intitle:"data engineer" AND (lead OR senior OR head)'
# Results per page
RESULTS = 100


def check_pos(obj: list, pos: int, failcase: str = "") -> str:
    """
    Check index in list, if not exists return failcase.
    :param obj: list
    :param pos: list's index
    :param failcase: case of IndexError
    :return:
    """
    try:
        return obj[pos]
    except IndexError as exc:
        return failcase


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        counter = 0
        rows = []

        while True:
            url = f"https://www.google.com/search?q={urllib.parse.quote(QUERY)}&num={RESULTS}&start={counter}"
            print(f"fetching {url}...")
            page.goto(url)
            time.sleep(3)

            if counter == 0:
                try:
                    page.locator('xpath=//button[@id="L2AGLb"]').click()
                except TimeoutError as exc:
                    pass

            results = page.query_selector_all('xpath=//div[@class="MjjYud"]')
            if not results:
                print(f"no more results...")
                break

            for result in results:
                # Get result title
                t = result.query_selector('xpath=//h3')
                try:
                    title = t.inner_text()
                    name = title.split('-')[0].strip()
                except Exception:
                    title = ""
                    name = ""

                # Get result url
                c = result.query_selector('xpath=//div[@class="yuRUbf"]/a')
                try:
                    href = c.get_attribute("href")
                except Exception as exc:
                    href = ""

                if "linkedin.com/in/" not in href:
                    continue

                # Get result sub title
                d = result.query_selector_all('xpath=//div[contains(@class,"MUxGbd wuQ4Ob WZ8Tjf")]//span')
                try:
                    spec = [x.inner_text() for x in d]
                    location = check_pos(spec, 0)
                    position = check_pos(spec, 2)
                    company = check_pos(spec, 4)
                except Exception as exc:
                    spec = []
                    location = ""
                    position = ""
                    company = ""

                rows.append({"title": title, "href": href, "spec": "".join(spec), "name": name, "location": location, "position": position, "company": company})

            # Update counter
            counter += RESULTS

        # Close browser window
        browser.close()

        # Export to csv
        df = pd.DataFrame(rows)
        # Print out an example
        print(df.iloc[0])
        df.to_csv("profiles.csv", index=False, encoding="utf8")

        print("Profiles retrieved successfully!")


if __name__ == '__main__':
    main()
