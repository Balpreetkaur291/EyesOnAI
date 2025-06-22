import os
import sys
import subprocess
import psutil
import pyautogui
import time
import shutil
import glob
from pathlib import Path
import platform
import json
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import google.generativeai as genai
from PIL import Image
from sfx import speak
import vapiassist


# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

class AccessibilityCommands:
    def __init__(self):
        self.system = platform.system().lower()
        self.browser_driver = None
    
    def start_vapi_call(self):
        print("Starting VAPI call...")
        vapiassist.make_outbound_call("vapi_id", "target_num")

    def regional_ocr_interactive(self):
        """Interactive regional OCR with immediate processing on mouse release"""
        import tkinter as tk
        from PIL import Image, ImageTk
        
        try:
            # Take a full screenshot first
            screenshot = pyautogui.screenshot()
            
            # Create overlay window
            root = tk.Tk()
            root.title("Select Region for OCR")
            root.attributes('-topmost', True)
            root.configure(bg='black')
            
            # Get screen dimensions
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            # Make window fullscreen
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            root.overrideredirect(True)  # Remove window decorations
            
            # Convert PIL image to PhotoImage for tkinter
            display_image = screenshot.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_image)
            
            # Create canvas
            canvas = tk.Canvas(root, width=screen_width, height=screen_height, 
                            highlightthickness=0, bg='black')
            canvas.pack()
            
            # Display screenshot
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            
            # Add semi-transparent overlay
            overlay_id = canvas.create_rectangle(0, 0, screen_width, screen_height, 
                                            fill='black', stipple='gray50')
            
            # Selection variables
            selection_rect = None
            start_x = start_y = current_x = current_y = 0
            ocr_result = None
            
            def start_selection(event):
                nonlocal start_x, start_y, selection_rect
                start_x, start_y = event.x, event.y
                if selection_rect:
                    canvas.delete(selection_rect)
                selection_rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, 
                                                    outline='red', width=10)
            
            def update_selection(event):
                nonlocal current_x, current_y, selection_rect
                current_x, current_y = event.x, event.y
                if selection_rect:
                    canvas.coords(selection_rect, start_x, start_y, current_x, current_y)
            
            def end_selection(event):
                nonlocal ocr_result
                if abs(current_x - start_x) > 10 and abs(current_y - start_y) > 10:
                    # Show processing message
                    canvas.delete("instruction")
                    root.update()  # Force update display
                    
                    try:
                        # Calculate actual coordinates on original screenshot
                        scale_x = screenshot.width / screen_width
                        scale_y = screenshot.height / screen_height
                        
                        x1 = int(min(start_x, current_x) * scale_x)
                        y1 = int(min(start_y, current_y) * scale_y)
                        x2 = int(max(start_x, current_x) * scale_x)
                        y2 = int(max(start_y, current_y) * scale_y)
                        
                        # Configure Gemini API
                        genai.configure(api_key=self.GEMINI_API_KEY)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Extract region from original screenshot
                        region = screenshot.crop((x1, y1, x2, y2))
                        
                        # Create prompt for OCR
                        prompt = """Please tell me what this image is in a concise simple way"""
                        
                        # Generate response
                        response = model.generate_content([prompt, region])
                        ocr_result = response.text.strip()
                        
                    except Exception as e:
                        ocr_result = f"OCR Error: {str(e)}"
                    
                    # Close the overlay immediately after processing
                    root.quit()
                else:
                    # Selection too small, show error briefly then continue
                    canvas.delete("instruction")
                    canvas.create_text(screen_width//2, screen_height//2, 
                                    text="Selection too small! Try again.", 
                                    fill='red', font=('Arial', 16, 'bold'), tags="error")
                    root.after(1500, lambda: canvas.delete("error"))  # Remove error after 1.5 seconds
                    root.after(1500, lambda: canvas.create_text(50, 50, text=instruction_text, 
                                            fill='white', font=('Arial', 12), anchor='nw', tags="instruction"))
            
            def on_hover(event):
                # Show coordinates on hover
                scale_x = screenshot.width / screen_width
                scale_y = screenshot.height / screen_height
                actual_x = int(event.x * scale_x)
                actual_y = int(event.y * scale_y)
                
                canvas.delete("hover_info")
                canvas.create_text(event.x + 10, event.y - 10, 
                                text=f"({actual_x}, {actual_y})", 
                                fill='white', font=('Arial', 10), tags="hover_info")
            
            def cancel(event=None):
                nonlocal ocr_result
                ocr_result = "OCR cancelled"
                root.quit()
            
            # Bind events
            canvas.bind('<Button-1>', start_selection)
            canvas.bind('<B1-Motion>', update_selection)
            canvas.bind('<ButtonRelease-1>', end_selection)  # OCR happens immediately on release
            canvas.bind('<Motion>', on_hover)
            root.bind('<Escape>', cancel)  # Keep ESC for emergency cancel only
            
            # Create instructions
            instructions = [
                "Regional OCR Selection",
                "",
                "• Click and drag to select region",
                "• OCR will run automatically when you release",
                "• Press ESC to cancel",
                "• Hover to see coordinates"
            ]
            
            instruction_text = "\n".join(instructions)
            canvas.create_text(50, 50, text=instruction_text, 
                            fill='white', font=('Arial', 12), anchor='nw', tags="instruction")
            
            # Run the overlay
            root.mainloop()
            
            # Clean up
            root.destroy()
            speak(ocr_result)

            return ocr_result if ocr_result else "No region selected"
            
        except Exception as e:
            return f"Error performing interactive regional OCR: {str(e)}"
    
    def ocr_screen(self):
        """Alternative OCR method that doesn't save to disk"""
        try:
            # Configure Gemini API
            genai.configure(api_key=self.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Take full screen screenshot
            screenshot = pyautogui.screenshot()
            
            # Create prompt for OCR
            prompt = """Please tell me what this image is in a concise simple way'."""
            
            # Generate response directly with PIL Image
            response = model.generate_content([prompt, screenshot])
            extracted_text = response.text.strip()
            speak(extracted_text)
            return f"OCR Text: {extracted_text}"
        except Exception as e:
            return f"Error performing screen OCR: {str(e)}"

    def ocr_coordinates(self, x, y, width, height):
        """Extract text from specific screen coordinates using OCR with Gemini Vision
        Args:
            x, y: top-left coordinates
            width, height: region dimensions
        """
        try:
            # Configure Gemini API
            genai.configure(api_key=self.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Take screenshot of specific region
            region = (x, y, width, height)
            screenshot = pyautogui.screenshot(region=region)
            screenshot_path = "temp_region_screenshot.png"
            screenshot.save(screenshot_path)
            
            # Load image
            image = Image.open(screenshot_path)
            
            # Create prompt for OCR
            prompt = """Please extract all text from this image. 
            Return only the extracted text without any additional commentary or formatting.
            If no text is found, return 'No text detected'."""
            
            # Generate response
            response = model.generate_content([prompt, image])
            extracted_text = response.text.strip()
            
            # Clean up temp file
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            
            return f"OCR Text from region ({x}, {y}, {width}, {height}): {extracted_text}"
            
        except Exception as e:
            return f"Error performing coordinate OCR: {str(e)}"
    # Window Management
    def open_application(self, app_name):
        """Open an application by name"""
        try:
            if self.system == "windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif self.system == "darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            else:  # Linux
                subprocess.Popen([app_name])
            return f"Successfully opened {app_name}"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    def close_application(self, app_name):
        """Close an application by name"""
        try:
            closed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed_count += 1
            if closed_count > 0:
                return f"Closed {closed_count} instance(s) of {app_name}"
            return f"Application {app_name} not found running"
        except Exception as e:
            return f"Error closing {app_name}: {str(e)}"
    
    def minimize_window(self):
        """Minimize the active window"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('win', 'down')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'm')
            else:
                pyautogui.hotkey('alt', 'F9')
            return "Active window minimized"
        except Exception as e:
            return f"Error minimizing window: {str(e)}"
    
    def maximize_window(self):
        """Maximize the active window"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('win', 'up')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'ctrl', 'f')
            else:
                pyautogui.hotkey('alt', 'F10')
            return "Active window maximized"
        except Exception as e:
            return f"Error maximizing window: {str(e)}"
    
    def switch_window(self):
        """Switch between open windows"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('alt', 'tab')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'tab')
            else:
                pyautogui.hotkey('alt', 'tab')
            return "Switched to next window"
        except Exception as e:
            return f"Error switching window: {str(e)}"
    
    def close_window(self):
        """Close the active window"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('alt', 'f4')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'w')
            else:
                pyautogui.hotkey('alt', 'f4')
            return "Active window closed"
        except Exception as e:
            return f"Error closing window: {str(e)}"
    
    def get_active_windows(self):
        """Get list of active windows for accessibility"""
        try:
            windows = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name']:
                    windows.append(proc.info['name'])
            unique_windows = list(set(windows))[:15]  # Limit to 15 for readability
            return f"Active applications: {', '.join(unique_windows)}"
        except Exception as e:
            return f"Error getting active windows: {str(e)}"

    # File Operations
    def create_file(self, filepath, content=""):
        """Create a new file"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            return f"Created file: {filepath}"
        except Exception as e:
            return f"Error creating file: {str(e)}"
    
    def create_folder(self, folderpath):
        """Create a new folder"""
        try:
            Path(folderpath).mkdir(parents=True, exist_ok=True)
            return f"Created folder: {folderpath}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"
    
    def delete_file(self, filepath):
        """Delete a file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return f"Deleted file: {filepath}"
            return f"File not found: {filepath}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    
    def delete_folder(self, folderpath):
        """Delete a folder and its contents"""
        try:
            if os.path.exists(folderpath):
                shutil.rmtree(folderpath)
                return f"Deleted folder: {folderpath}"
            return f"Folder not found: {folderpath}"
        except Exception as e:
            return f"Error deleting folder: {str(e)}"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Error copying file: {str(e)}"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source, destination)
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Error moving file: {str(e)}"
    
    def rename_file(self, old_path, new_path):
        """Rename a file or folder"""
        try:
            os.rename(old_path, new_path)
            return f"Renamed {old_path} to {new_path}"
        except Exception as e:
            return f"Error renaming: {str(e)}"
    
    def search_files(self, directory, pattern):
        """Search for files matching a pattern"""
        try:
            matches = glob.glob(os.path.join(directory, f"**/*{pattern}*"), recursive=True)
            if matches:
                return f"Found {len(matches)} files: {', '.join(matches[:10])}"
            return f"No files found matching '{pattern}' in {directory}"
        except Exception as e:
            return f"Error searching files: {str(e)}"
    
    def list_directory(self, directory="."):
        """List contents of a directory"""
        try:
            items = os.listdir(directory)
            folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
            files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
            return f"Directory {directory}:\nFolders: {', '.join(folders[:10])}\nFiles: {', '.join(files[:10])}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def set_brightness(self, level):
        """Set screen brightness (0-100) - Windows only"""
        try:
            if self.system == "windows":
                subprocess.run(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})", shell=True)
                return f"Brightness set to {level}%"
            else:
                return "Brightness control not implemented for this OS"
        except Exception as e:
            return f"Error setting brightness: {str(e)}"
    
    def shutdown_system(self):
        """Shutdown the computer"""
        try:
            if self.system == "windows":
                subprocess.run("shutdown /s /t 5", shell=True)
            elif self.system == "darwin":
                subprocess.run("sudo shutdown -h +1", shell=True)
            else:
                subprocess.run("shutdown -h +1", shell=True)
            return "System will shutdown in 1 minute"
        except Exception as e:
            return f"Error shutting down: {str(e)}"
    
    def restart_system(self):
        """Restart the computer"""
        try:
            if self.system == "windows":
                subprocess.run("shutdown /r /t 5", shell=True)
            elif self.system == "darwin":
                subprocess.run("sudo shutdown -r +1", shell=True)
            else:
                subprocess.run("shutdown -r +1", shell=True)
            return "System will restart in 1 minute"
        except Exception as e:
            return f"Error restarting: {str(e)}"

    # Browser Operations
    def init_browser(self):
        """Initialize browser driver"""
        try:
            if not self.browser_driver:
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.browser_driver = webdriver.Chrome(options=options)
            return "Browser initialized"
        except Exception as e:
            return f"Error initializing browser: {str(e)}"
    
    def open_url(self, url):
        """Open a URL in the browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return f"Opened URL: {url}"
        except Exception as e:
            return f"Error opening URL: {str(e)}"
    
    def browser_back(self):
        """Go back in browser"""
        try:
            if self.browser_driver:
                self.browser_driver.back()
                return "Navigated back"
            else:
                pyautogui.hotkey('alt', 'left')
                return "Navigated back using keyboard shortcut"
        except Exception as e:
            return f"Error going back: {str(e)}"
    
    def browser_forward(self):
        """Go forward in browser"""
        try:
            if self.browser_driver:
                self.browser_driver.forward()
                return "Navigated forward"
            else:
                pyautogui.hotkey('alt', 'right')
                return "Navigated forward using keyboard shortcut"
        except Exception as e:
            return f"Error going forward: {str(e)}"
    
    def refresh_page(self):
        """Refresh the current page"""
        try:
            if self.browser_driver:
                self.browser_driver.refresh()
                return "Page refreshed"
            else:
                pyautogui.hotkey('ctrl', 'r')
                return "Page refreshed using keyboard shortcut"
        except Exception as e:
            return f"Error refreshing page: {str(e)}"
    
    def new_tab(self):
        """Open a new tab"""
        try:
            pyautogui.hotkey('ctrl', 't')
            return "New tab opened"
        except Exception as e:
            return f"Error opening new tab: {str(e)}"
    
    def close_tab(self):
        """Close the current tab"""
        try:
            pyautogui.hotkey('ctrl', 'w')
            return "Tab closed"
        except Exception as e:
            return f"Error closing tab: {str(e)}"
    
    def switch_tab(self, direction="next"):
        """Switch to next or previous tab"""
        try:
            if direction == "next":
                pyautogui.hotkey('ctrl', 'tab')
            else:
                pyautogui.hotkey('ctrl', 'shift', 'tab')
            return f"Switched to {direction} tab"
        except Exception as e:
            return f"Error switching tab: {str(e)}"

    # Accessibility Features
    def read_screen(self, x=None, y=None):
        """Take a screenshot and describe coordinates"""
        try:
            screenshot = pyautogui.screenshot()
            if x and y:
                pixel_color = screenshot.getpixel((x, y))
                return f"Pixel at ({x}, {y}) has color RGB{pixel_color}"
            else:
                screenshot.save("current_screen.png")
                return "Screenshot saved as current_screen.png"
        except Exception as e:
            return f"Error reading screen: {str(e)}"
    
    def click_at(self, x, y):
        """Click at specific coordinates"""
        try:
            pyautogui.click(x, y)
            return f"Clicked at coordinates ({x}, {y})"
        except Exception as e:
            return f"Error clicking at coordinates: {str(e)}"
    
    def type_text(self, text):
        """Type text at current cursor position"""
        try:
            pyautogui.write(text)
            return f"Typed: {text}"
        except Exception as e:
            return f"Error typing text: {str(e)}"
    
    def press_key(self, key):
        """Press a specific key or key combination"""
        try:
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            return f"Pressed key: {key}"
        except Exception as e:
            return f"Error pressing key: {str(e)}"
    
    def scroll(self, direction="down", clicks=3):
        """Scroll in a direction"""
        try:
            if direction == "down":
                pyautogui.scroll(-clicks)
            else:
                pyautogui.scroll(clicks)
            return f"Scrolled {direction} {clicks} clicks"
        except Exception as e:
            return f"Error scrolling: {str(e)}"

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.browser_driver:
                self.browser_driver.quit()
            return "Cleanup completed"
        except Exception as e:
            return f"Error during cleanup: {str(e)}"
        
if __name__ == "__main__":
    AccessibilityCommands().regional_ocr_interactive()
