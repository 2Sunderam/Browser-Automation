
from browser_use import Agent, Browser, BrowserConfig,Controller, ActionResult
from dotenv import load_dotenv
import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Any

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
        task="Navigate to https://staging-csp-portal.leapscholar.com/profile/23540?key=PROFILE and wait for the page to load completely.",
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
         In the Profile Information section:
        1. First locate and click the edit button at the top of the form

        2. General Details (look for the "General Details" heading):
           - Select Gender: Click dropdown, select 'Female' from the options
           - Set Date of birth to '13-09-2003'
           - Enter Passport Number '564432218654'
           - Select Issue Country: type India, in dropdown India appears, select 'India'
           - For Select Issue State: type Jharkhand, in dropdown Jharkhand appears, select 'Jharkhand'
           - For Select Marital Status: Click dropdown, select 'Single'
           Scroll the page down 60 pixels and check continuously until the fields like "Select Lead Quality","Follow Up Date", etc fields are visible and fill these fields with the data.

        3. Lead Details (immediately below General Details):
           - For Select Lead Quality: Click dropdown, select 'Warm'
           - Fill Follow Up Date to '13-09-2025'
           - For Counsellor Name: Click dropdown, select 'Select All'
           - Enter 'Canada' in Select Search by Key field
           - For Sub Agent: Click dropdown, select 'aaa'
           - Set Lead Source to 'Unisetu'
           Scroll the page 60 pixels and check continuously until the fields like "Enter Name","Enter Email",etc fields are found and fill those field with the data .
        4. Emergency Contact Details:
           - Enter Emergency Contact "Enter Name" field as "Jatan Jain"
           - Set Emergency Contact Email "Enter Email" field to 'jatan@gmail.com'
           - Set Emergency Contact Number "Enter Contact Number" to '9932412212'
           - For Select Relationship field: Click dropdown, select 'Sibling'

        5. Saving the form:
           - Scroll the page up slowly and check continuously until the "Save" button is found and then click to save the details.
           - Click the save button
        Important Notes:
        - Verify each field is visible before interacting
        - Wait for dropdown options to appear before selecting
        - Confirm each section heading before filling fields""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()

async def fill_student_preferences(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Student Preferences section: Click on the edit button, 
        Preferred Country dropdown menue: Choose Canada , Preferred Intake dropdown: Select September 2025, 
        Preferred Degree dropdown: Select Ph.D.,Preferred Course Dropdown: Select Agronomy. click save. Scroll 60 pixels continuosly to make more fields visible""",
        browser_context=browser_context,
        use_vision=True
    )
    return await agent.run()


# Create controller with file upload action
controller = Controller()

@controller.action('upload_file')
async def upload_file(page: Any, file_path: str) -> ActionResult:
    try:
        # Wait for the upload button to be visible and enabled
        # Using a more general selector for the button text
        upload_button = await page.wait_for_selector('button:has-text("Upload Document")', state='visible', timeout=10000)
        if not upload_button:
             return ActionResult(success=False, message="Upload Document button not found")

        # Wait for the file chooser dialog to appear after clicking the button
        async with page.context.expect_filechooser() as fc_info:
             await upload_button.click()

        file_chooser = await fc_info.value

        # Set the file(s) on the file chooser
        await file_chooser.set_files(file_path)

        # Wait for a reasonable time for the upload to process and UI to update
        # This timeout might need adjustment based on upload speed and server response
        await page.wait_for_timeout(5000)

        # Verify upload completion - look for the filename in the DOM
        file_name = file_path.split('\\')[-1]
        try:
            # Wait for the file name to appear on the page as a confirmation
            await page.wait_for_selector(f'text="{file_name}"', timeout=15000)
            # You might also want to wait for a progress indicator to disappear
            # or a success message to appear, depending on the website's UI.
            # Example: await page.wait_for_selector('.upload-progress-spinner', state='hidden', timeout=10000)
            return ActionResult(success=True, message="File uploaded successfully")
        except Exception:
            # If the file name doesn't appear within the timeout, assume failure
            return ActionResult(success=False, message=f"File name '{file_name}' did not appear on the page after upload.")

    except Exception as e:
        return ActionResult(success=False, message=f"File upload failed: {str(e)}")

async def fill_academic_info(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="""In the Academic Information section: Click edit,
         Onece the fields are visible, immediately start filling the fields with the data below:
          Fill Select Qualification field: Type "Bachelors degree" then a dropdown will appear Select the Bachelors degree from the dropdown,
          Left of that will be Select gap in studies field: Click dropdown, select '0'.
          left of that will be the Enter Years of education Field: Type 4,
          ##Below the above details new field will appear, fill those fields as:
          Select Degree Type field : type "BA" then a dropdown will appear Select the BA from the dropdown,
          Select Degree Specialisation field: Type "Agricultural Science" then a dropdown will appear Select the Agricultural Science from the dropdown,
          Select grading Scheme field: Click on the fied and select "CGPA" from the dropdown,
          Enter Grades field: Type 8.5, 
          Do you have backlogs- Select Yes/No field: Select No,
          Select Accridation field: Click on the fied and select "A++" from the dropdown,  
          Select University field: Type "University of Delhi" then a dropdown will appear Select the "University of Delhi" from the dropdown,
          Documents field: Type UG Eight Sem Mark Sheet and then a dropdown will appear Select the "UG Eight Sem Mark Sheet" from the dropdown,
          For the Documents field: Use the upload_file action with path: "c:\\Users\\91787\\Documents\\Browser automation\\Sunderam Dutta portfolio.pdf"
          
          Scroll up to find the save button and Click the save button""",  
        browser_context=browser_context,
        controller=controller,
        extend_system_message = """
        Always Scroll 60 pixels at a time and then check for the correct field, scroll up, down as needed, remember scrolling is there for navigating and finding the correct fields. First two sections are the Profile information, Student Preferences, the the Academic Information section starts where you fill the details.
         """,
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
        model="gemini-2.5-pro-preview-05-06",  # Updated to use gemini-2.0-flash-exp
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

        # Phase 1: Navigation
        print("\n=== Navigation ===")
        print("Navigating to student profile...")
        await navigate_to_profile(context, llm)
        print("Navigation completed")
        await asyncio.sleep(3)  # Wait for page to load completely

        # Phase 2: Profile Information
        print("\n=== Profile Information ===")
        print("Filling profile information...")
        await fill_profile_info(context, llm)
        print("Profile information completed")
        await asyncio.sleep(2)

        # Phase 3: Student Preferences
        print("\n=== Student Preferences ===")
        print("Filling student preferences...")
        await fill_student_preferences(context, llm)
        print("Student preferences completed")
        await asyncio.sleep(2)

        # Phase 4: Academic Information
        print("\n=== Academic Information ===")
        print("Filling academic information...")
        await fill_academic_info(context, llm)
        print("Academic information completed")

        print("\nAll tests completed successfully")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())