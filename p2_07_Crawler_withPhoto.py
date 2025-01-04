from playwright.async_api import async_playwright
import pandas as pd
import asyncio
import random
import datetime
import warnings
import sys
import httpx
import os
import gc


async def timer(sleeptime, step_name):
    for i in reversed(range(sleeptime)):
        sys.stderr.write(f'\r%4d seconds left {step_name}' % i)
        await asyncio.sleep(1)


async def human_simulator(page, step_name):
    print(f"\n    👍 Conducting Human Simulator Operations, {step_name} ")
    await timer(sleeptime, step_name)
    await page.mouse.move(100, 500)
    await page.mouse.down()
    await page.mouse.move(500, 900)
    await page.mouse.up()


async def download_image(url, filename):
    if url.startswith('//'):
        url = 'http:' + url
    try:
        r = await client.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)
    except httpx.UnsupportedProtocol:
        print(" - Invalid photo file ...")


async def image_page(pic_url, page, id_number):
    print('\n  - pictures page : ', pic_url)
    try:
        await page.goto(pic_url, timeout=60000)
        image_directory = 'img3'
        os.makedirs(image_directory, exist_ok=True)
        local_address = os.path.join(image_directory, str(id_number))
        os.makedirs(local_address, exist_ok=True)
        full_address = os.path.abspath(local_address)
        step_name = "in image_page"
        await human_simulator(page, step_name)

        data = {}
        data['full_address'] = full_address
        data['local_address'] = local_address
        await d_submit(data, id_number)  # submit

        div_element = await page.query_selector("#pictures-list")
        image_elements = await div_element.query_selector_all("img")
        for i, image_element in enumerate(image_elements):
            image_url = await image_element.get_attribute("src")
            if image_url is not None:
                await download_image(image_url, os.path.join(local_address, f"image_{i}.jpg"))
        print(f'     ✔ stored pictures:  {local_address}')
        print(f'     ✔ full address:  {full_address}')
        return local_address, full_address
    except:
        step_name = " ==> state: in Reloading image_page !!"
        await timer(10, step_name)
        await image_page(pic_url, page, id_number)


async def d_submit(data, id_number):
    df = pd.read_csv(mydb, index_col="id_number")
    warnings.filterwarnings("ignore", category=FutureWarning)
    df = df.apply(lambda x: x.strip() if isinstance(x, str) else x)
    new_data = pd.DataFrame(data, index=[id_number])
    if id_number in df.index:
        df.update(new_data)
    else:
        df = pd.concat([df, new_data])
    try:
        df.to_csv(mydb, index=True, index_label='id_number')
    except PermissionError:
        print(
            "\n  ❌ Permission/access to csv file is not possible. \n\n     It will be tried again in 10 seconds ❗ ")
        step_name = "==> state: Submitting data !"
        await timer(10, step_name)
        try:
            df.to_csv(mydb, index=True, index_label='id_number')
        except PermissionError:
            print("\n  ❌ Permission/access to csv file is still not possible. ")
            exit()
    print(f"     ✔ Data Submitted in 'CSV' file! ")
    gc.collect()
    return id_number


async def text_gathering(page, main_url, pic_url, id_number):
    try:
        await page.goto(main_url, timeout=60000)
        data = {}
        ct = datetime.datetime.now()
        ts = ct.timestamp()
        head_content = await page.eval_on_selector("head", "e => e.innerHTML")
        if head_content.strip() != "":
            product_name = await page.evaluate(
                '() => document.querySelector("h1.specs-phone-name-title")?.textContent')
            print(f'\n  - Now data_gathering for : "{product_name}"')
            await page.wait_for_selector("div#specs-list")
            comment = await page.evaluate('() => document.querySelector("p[data-spec=\\"comment\\"]")?.textContent')

            data['product_name'] = product_name
            data['main_url'] = main_url
            data['pic_url'] = pic_url
            data['lastupdate'] = str(ct)
            data['timestamp'] = str(ts)
            data['comment'] = comment

            tables = await page.query_selector_all("table[cellspacing='0']")
            previous_ttl = None
            for table in tables:
                rows = await table.query_selector_all("tr")
                for row in rows:
                    ttl_element = await row.query_selector(".ttl")
                    if ttl_element is not None:
                        ttl_html = await ttl_element.inner_html()
                        ttl_text = await ttl_element.inner_text()
                        ttl = ttl_text if '</a>' in ttl_html else ttl_html

                        if ttl == '&nbsp;':  # &nbsp;
                            ttl = previous_ttl + '_n'
                        previous_ttl = ttl

                        nfo_element = await row.query_selector(".nfo")
                        if nfo_element is not None:
                            nfo_html = await nfo_element.inner_html()
                            nfo_text = await nfo_element.inner_text()
                            nfo = nfo_text if '</a>' in nfo_html else nfo_html
                            data[ttl] = nfo
            await d_submit(data, id_number)  # submit
            step_name = "in main page ==> state: text_gathering done!"
            await human_simulator(page, step_name)
            await image_page(pic_url, page, id_number)

        else:
            print(f' - id_number: {id_number}  Not Found !')
            data['product_name'] = 'Not Found'
            data['main_url'] = main_url
            data['lastupdate'] = str(ct)
            data['timestamp'] = str(ts)
            data['comment'] = ''
            await d_submit(data, id_number)  # submit
            step_name = "in main page ==> state: Not Found text!"
            await human_simulator(page, step_name)

    except:
        PlaywrightTimeoutError: (print("Timeout!"))
        print(" * Timeout! -- please check your internet !\n")
        step_name = "in main page ==> state: Timeout!"
        await timer(20, step_name)
        await text_gathering(page, main_url, pic_url, id_number)



async def run(playwright):
    browser = await playwright.chromium.launch()
    for id_number in range(start, end):  # Limit
        main_url = f'https://www.gsmarena.com/x-{id_number}.php'
        pic_url = f'https://www.gsmarena.com/x-pictures-{id_number}.php'
        print('=' *70)
        print(' >> main_page link : ', main_url, '    - time:', datetime.datetime.now().strftime("%H:%M:%S"))
        context = await browser.new_context()
        page = await context.new_page()
        await text_gathering(page, main_url, pic_url, id_number)  # text_gathering
        await context.close()
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        try:
            await run(playwright)
        except AttributeError as e:
            print("initializer.get('parentFrame') returned error ".format(e))
            raise e


start = 4088
end = 4091
mydb = 'dataset02.csv'
sleeptime = int(random.uniform(11, 14))

client = httpx.AsyncClient()
asyncio.run(main())
