from browser_use import Browser, BrowserConfig
import asyncio

async def upload_file(file_path: str):
    try:
        browser = Browser(
            config=BrowserConfig(
                browser_binary_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                headless=False,
                viewport_size={"width": 1920, "height": 1080},
                persistent_context_dir="./browser_data",
                ignore_https_errors=True,
                timeout=60000
            )
        )
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://staging-csp-portal.leapscholar.com/profile/23540?key=PROFILE")
        await page.click('button:has-text("Browse from Computer")')
        await page.locator('input[type="file"]').set_input_files(file_path)
        await asyncio.sleep(8)
        print("File uploaded successfully")
        await context.close()
        await browser.close()
        return {"success": True, "message": "File uploaded successfully"}
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return {"success": False, "message": f"Upload failed: {str(e)}"}

async def main():
    file_path = r"c:\\Users\\91787\\Documents\\Browser automation\\Sunderam Dutta portfolio.pdf"
    await upload_file(file_path)

if __name__ == "__main__":
    asyncio.run(main())