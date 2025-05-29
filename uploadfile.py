from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import (
    Agent,
    Browser,
    BrowserConfig,
    Controller,      # Import Controller
    ActionResult,
       # Import ActionResult
)
from pydantic import BaseModel, Field 
from playwright.async_api import Page # Import Page for type hinting in custom action
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# --- Define Controller and Custom Action Globally or in Main ---
controller = Controller()
FILE_TO_UPLOAD = r"c:\Users\91787\Documents\Browser automation\Sunderam Dutta portfolio.pdf" # Define file path

controller = Controller()
FILE_TO_UPLOAD = r"c:\Users\91787\Documents\Browser automation\Sunderam Dutta portfolio.pdf"

# --- Define a Pydantic model for the parameters the LLM needs to provide ---
class UploadFileParams(BaseModel):
    file_path: str = Field(description="The absolute path to the file that needs to be uploaded.")



@controller.action(
    'Upload a file to a visible file input element on the page',
    param_model=UploadFileParams
)
# Change signature: Receive BrowserContext
async def upload_file(params: UploadFileParams, browser_context: BrowserConfig) -> ActionResult:
    """
    Attempts to upload a file using a standard file input element.
    The LLM should ensure a file input is ready (e.g., after clicking a 'browse' button)
    before calling this action, and provide the file_path.
    """
    # Get the current page from the browser_context
    # This assumes the agent is primarily interacting with one page
    pages = browser_context.pages
    if not pages:
         return ActionResult(
            extracted_content="Could not access any page via browser_context.",
            include_in_memory=False
        )
    # Get the most likely "current" page the agent is viewing
    # Playwright often lists the most recently interacted page last or first,
    # but .pages[0] is a common heuristic if you expect only one main tab.
    # A more robust approach might be to get the page by URL or title if known.
    page = pages[0] # Adjust if your agent uses multiple tabs actively

    file_path = params.file_path # Access file_path from the params model

    try:
        # Now use the obtained 'page' object for Playwright interactions
        file_input = await page.query_selector('input[type="file"]:not([style*="display: none"])')

        if not file_input:
            all_file_inputs = await page.query_selector_all('input[type="file"]')
            if not all_file_inputs:
                return ActionResult(
                    extracted_content="No file input element ('input[type=\"file\"]') found on the page.",
                    include_in_memory=False
                )
            file_input = all_file_inputs[0]
            print("Found a hidden file input, attempting to make it interactable.")
            await page.evaluate("""
                (element) => {
                    element.style.display = 'block !important';
                    element.style.visibility = 'visible !important';
                    element.style.opacity = '1 !important';
                    element.style.width = '1px !important';
                    element.style.height = '1px !important';
                    element.style.position = 'fixed !important';
                    element.style.top = '0 !important';
                    element.style.left = '0 !important';
                    element.style.zIndex = '999999 !important';
                }
            """, file_input)
            await page.wait_for_timeout(500)

        if not await file_input.is_visible():
             print(f"File input element is not visible or interactable after attempting to force it.")

        print(f"Attempting to set input files: {file_path} on element.")
        await file_input.set_input_files(file_path)
        await page.wait_for_timeout(3000)

        return ActionResult(
            extracted_content=f"Attempted to set file input with: {file_path}. The page should now reflect this selection if successful.",
            include_in_memory=True
        )
    except Exception as e:
        print(f"Error in upload_file action: {e}")
        return ActionResult(
            extracted_content=f"Upload file action failed: {str(e)}",
            include_in_memory=False
        )

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

async def edit_and_upload_student_details(browser_context, llm, current_controller, file_to_upload_path):
    agent = Agent(
        llm=llm,
        task=""" Navigate to https://staging-csp-portal.leapscholar.com/profile/23540?key=PROFILE url and student dahboard will appear. 
    1. First, scroll down by 600 pixels continously, in the page carefully until the "All Documents" section is clearly visible.
    2. Within the "Upload All Docs" section, locate and click the element that allows you to choose a file from your computer. This might be a button labeled "Browse from Computer", "Upload Document", "Add Document", an icon, or the area itself if it's clickable.
    3. After clicking the element to initiate file selection, use the 'upload_file' tool with the following file path:
       `{file_to_upload_path}`
       Make sure to pass the file_path exactly as provided to the tool.
    4. After using the 'upload_file' tool, observe the page for any indication that the file has been selected (e.g., the filename "{os.path.basename(file_to_upload_path)}" appearing on the page). Report if you see the filename.""",
        browser_context=browser_context,
        use_vision=True,
        controller=current_controller, # Pass the controller with the upload_file action
        enable_memory=True, # Good for multi-step tasks like this
    )
    await agent.run()
    

async def main():
    browser = None
    context = None
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    try:
        browser = await setup_browser()
        # Use a newer or recommended model if available and suitable
        llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-preview-04-17', google_api_key=google_api_key)
        
        context = await browser.new_context()  
        
        print("Editing student details and uploading document...")
        # Pass the globally defined controller and file path to the agent function
        await edit_and_upload_student_details(context, llm, controller, FILE_TO_UPLOAD)
        print("Student details editing and document upload attempt completed.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())