
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

async def setup_browser():
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
    return browser

async def navigate_to_profile(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="Navigate to https://staging-csp-portal.leapscholar.com/profile/23541?key=PROFILE and wait for the page to load completely.",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

# Keep the first definition of fill_profile_info
async def fill_profile_info(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Profile Information section:
        1. First locate and click the edit button at the top of the form

        2. General Details (look for the "General Details" heading):
           - For Gender: Click dropdown, select 'Female' from visible options
           - Set Date of birth to '13-09-2003'
           - Enter Passport Number '564432218654'
           - For Issue Country: type India, in dropdown India appears, select 'India'
           - For Issue State: type Jharkhand, in dropdown Jharkhand appears, select 'Jharkhand'
           - For Marital Status: Click dropdown, select 'Single'
           Scroll the page down slowly and check continuously until the "Lead Details" heading appears.

        3. Lead Details (immediately below General Details):
           - For Lead Quality: Click dropdown, select 'Warm'
           - Fill Follow Up Date to '13-09-2025'
           - For Counsellor Name: Click dropdown, select 'Select All'
           - Enter 'Canada' in Search by Key field
           - For Sub Agent: Click dropdown, select 'aaa'
           - Set Lead Source to 'Unisetu'
           Scroll the page down slowly and check continuously until the "Emergency Contact Details" heading appears.
        4. Emergency Contact Details:
           - Enter Emergency Contact Name as "Jatan Jain"
           - Set Emergency Contact Email to 'jatan@gmail.com'
           - Set Emergency Contact Number to '9932412212'
           - For Relationship: Click dropdown, select 'Sibling'

        5. Saving the form:
           - Scroll the page up slowly and check continuously until the "Save" button is visible and then cliock to save the details.
           - Click the save button
        Important Notes:
        - Verify each field is visible before interacting
        - Wait for dropdown options to appear before selecting
        - Confirm each section heading before filling fields""",
        browser_context=browser_context,
        use_vision=False
    )
    return await agent.run()

async def fill_student_preferences(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Student Preferences section: Click edit, Select Preferred Country as Canada, Intake as Fall 2024, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_academic_info(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Academic Information section: Click edit, fill Last education as Bachelor's degree, Field of study as Computer Science, CGPA as 8.5, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_test_info(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Test Information section: Click edit, fill GRE Score as 320, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_english_exam(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the English Exam Details section: Click edit, select IELTS Academic, Overall Score as 7.5, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_work_info(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Work Information section: Click edit, fill Work Experience as 2 years in Software Development, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def upload_documents(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the All Documents section: Click edit, verify the document upload section is visible, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_address(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Address Details section: Click edit, fill Current Address and Permanent Address fields, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_passport(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Passport Details section: Click edit, fill Passport Number as A1234567, Expiry Date as 01/01/2030, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_background(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Background Details section: Click edit, fill any relevant background information, click save.""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",  # Updated to use gemini-2.0-flash-exp
        google_api_key=api_key,
        temperature=0.1,
        use_vision=True
    )

async def main():
    browser = None
    context = None
    try:
        browser = await setup_browser()
        llm = await get_llm()
        context = await browser.new_context()

        # Test Phase 1: Initial Navigation
        print("\n=== Testing Navigation ===")
        print("Navigating to student profile...")
        await navigate_to_profile(context, llm)
        print("Navigation completed")
        await asyncio.sleep(3)  # Wait for page to load completely

        # Test Phase 2: Profile Information
        print("\n=== Testing Profile Information ===")
        print("Starting to fill Profile Information...")
        await fill_profile_info(context, llm)
        print("Profile Information completed")

        print("\nInitial testing phase completed successfully")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())