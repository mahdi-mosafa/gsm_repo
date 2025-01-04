from playwright.async_api import async_playwright
import pandas as pd
import asyncio
import random
import datetime
import warnings
import sys
import httpx
import gc


async def timer(sleeptime):
    for i in reversed(range(sleeptime)):
        sys.stderr.write('\r%4d seconds left' % i)
        await asyncio.sleep(1)


async def human_simulator(page):
    print("    👍 Conducting Human Simulator Operations . . .  ")
    await timer(sleeptime)
    await page.mouse.move(100, 500)
    await page.mouse.down()
    await page.mouse.move(500, 900)
    await page.mouse.up()


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
        await timer(10)
        try:
            df.to_csv(mydb, index=True, index_label='id_number')
        except PermissionError:
            print("\n  ❌ Permission/access to csv file is still not possible. ")
            exit()
    print(f"\n ✔ Submitted in 'CSV' file! ")
    print('------------------------------------------------')
    gc.collect()  # Call the garbage collector
    return id_number


async def text_gathering(page, final_url, pic_url, id_number):
    try:
        await page.goto(final_url, timeout=120000)
        await human_simulator(page)
        data = {}
        ct = datetime.datetime.now()
        ts = ct.timestamp()
        print('  - time:', ct.strftime("%H:%M:%S"))
        head_content = await page.eval_on_selector("head", "e => e.innerHTML")
        if head_content.strip() != "":
            product_name = await page.evaluate('() => document.querySelector("h1.specs-phone-name-title")?.textContent')
            await page.wait_for_selector("div#specs-list")
            comment = await page.evaluate('() => document.querySelector("p[data-spec=\\"comment\\"]")?.textContent')

            data['product_name'] = product_name
            data['final_url'] = final_url
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

        else:
            print(f' - id_number: {id_number}  Not Found !')
            data['product_name'] = 'Not Found'
            data['final_url'] = final_url
            data['lastupdate'] = str(ct)
            data['timestamp'] = str(ts)
            data['comment'] = ''
            await d_submit(data, id_number)  # submit
    except:
        PlaywrightTimeoutError: (print("Timeout!"))
        print(" * Timeout! -- please check your internet !\n")
        await timer(30)
        await text_gathering(page, final_url, pic_url, id_number)


async def run(playwright):
    browser = await playwright.chromium.launch()
    for id_number in range(start, end):  # Limit
        final_url = f'https://www.gsmarena.com/x-{id_number}.php'
        pic_url = f'https://www.gsmarena.com/x-pictures-{id_number}.php'
        print('\n >> product link : ', final_url)
        print('  - pictures page : ', pic_url, '\n')
        context = await browser.new_context()
        page = await context.new_page()
        await text_gathering(page, final_url, pic_url, id_number)  # text_gathering
        await context.close()
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        try:
            await run(playwright)
        except AttributeError as e:
            print("initializer.get('parentFrame') returned error ".format(e))
            raise e


start = 4025
end = 4040
mydb = 'dataset02.csv'
sleeptime = int(random.uniform(11, 14))

client = httpx.AsyncClient()
asyncio.run(main())
