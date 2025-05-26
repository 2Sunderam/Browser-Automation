from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
load_dotenv()
import asyncio

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

async def create_student(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="go to https://staging-csp-portal.leapscholar.com/summary-dashboard, find the Add New Student button in the dashboard and click on it, then a popup form will open up, your job is to fill the form and submit it. Here is the form details: Given Name*= keshav , Last Name*=  jain, Mobile Number*= 9423527223, remember mobile number is Indian so the dropdown will be 91, Email= keshav@gmail.com, select sub agent= No sub agent this will be a dropdown, click on Enable student login for this profile and then lastly click create student button on the bottom left, also a pop up with confirmation will come after the task is done click on the confirmation button.",
        browser_context=browser_context, # Pass the shared context
        use_vision=True
    )
    await agent.run()
    # No need to return the agent instance here
    # return agent

async def edit_student_details(browser_context, llm):
    agent = Agent(
        llm=llm,
        task="A large form will open As student dashboard These are all the parts of the form 1.Profile information, 2.Student Preferences 3.Academic Information 4.Test Information 4.English Exam Details, 5.Work Information, 6.All Documents,7.Address Details 8.Passport Details 9.Background Details 10.Personal Notes about student for self-reference. your job is to scroll from top to bottom and click the edit buttons on each section of the form, the edit button will be on the top right hand corner of each section and the scrool back up to the top.",
        browser_context=browser_context, # Pass the shared context
        use_vision=True
    )
    return await agent.run()

async def main():
    browser = None
    context = None # Initialize context variable
    try:
        browser = await setup_browser()
        llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-preview-05-20')
        
        # Create a shared browser context from the browser instance
        context = await browser.new_context()
        
        print("Creating new student...")
        # Pass the shared context to the first agent function
        await create_student(context, llm)
        print("Student creation completed.")
        
        await asyncio.sleep(3) # Keep the delay
        
        print("Editing student details...")
        # Pass the *same* shared context to the second agent function
        await edit_student_details(context, llm)
        print("Student details editing completed.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the context before closing the browser
        if context:
            await context.close()
        if browser:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())