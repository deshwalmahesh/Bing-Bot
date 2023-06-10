from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
import pandas as pd
import numpy as np
from gtts import gTTS
from tqdm import tqdm
import re, time, subprocess, psutil
from multiprocessing import cpu_count
from pandarallel import pandarallel


pandarallel.initialize(nb_workers=cpu_count()-1)


def kill_all_existing_webdrivers(name = 'msedge'):
    '''
    This function kills all processes with the given name
    '''
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            try:
                proc.kill()
            except psutil.AccessDenied:
                print(f"Access denied to kill process {proc.info['pid']}.")
            except Exception as e:
                print(f"An error occurred while trying to kill process {proc.info['pid']}: {e}")



class BingGPT4:
    def __init__(self, edge_webdriver = None, tone:str = "precise", wait_time:float = 45):
        '''
        Open Edge Beta to interact with Bing chat
        args:
            edge_webdriver: Either a driver object of type: selenium.webdriver.edge.webdriver.WebDriver or the path to the edge webdriver
            tone: One of ['precise', 'balanced', 'creative']
            wait_time = Wait time in seconds before sending the next query to bot. Bigger the query, slower the response. So you have to increase or decrease it
        '''
        if not isinstance(edge_webdriver, (webdriver.edge.webdriver.WebDriver, webdriver.edge.service.Service, str)): assert False, "Either provide an Selenium Edge WebDriver, or Service object or the path to webdriver"
        
        if isinstance(edge_webdriver, webdriver.edge.service.Service):
            kill_all_existing_webdrivers()
            self.driver= webdriver.Edge(service = edge_webdriver)
        elif isinstance(edge_webdriver, str):
            kill_all_existing_webdrivers()
            self.driver= webdriver.Edge(edge_webdriver)
        else: self.driver = edge_webdriver

        self.driver.maximize_window()
        self.tone = "DEFAULT" # Tone of the model. If not set as DEFAULT  then it won't load the user desired for the first time
        self._reload_bing_chat(tone) # Open Chat for first time use

        self.limit_counter = 0 # there is a limit of 5 messages and then it has to be reload again
        self.chat_history = [] # (query, response)
        self.wait_time = wait_time # Wait after sending a query to bot
        self.timer_start = time.time() #Timer to adjust the wait_time
        self.total_interactions = 0


    def _reload_bing_chat(self, tone):
        '''
        Reload bing chat and access it's chat box. There are limits to no of message as 5. so reset the limit
        args:
            tone: Tone of the model
        '''
        self.driver.get("https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx") # Get bing chat
        time.sleep(4)
        self._change_tone(tone)

        reach_chatbox_box_script = """
        return document.querySelector('cib-serp').shadowRoot
        .querySelector('cib-action-bar').shadowRoot
        .querySelector('textarea[name="searchbox"]')
        """
        self.chat_box = self.driver.execute_script(reach_chatbox_box_script)
        self.limit_counter = 0 # Reset the limit after reload


    def _change_tone(self, tone:str="precise"):
        '''
        Change the tone of the current model. Only works if existing tone is different from given
        '''
        tone = tone.lower()

        if tone != self.tone:
            print(f"Changing Tone from {self.tone} to {tone}")
            self.tone = tone
            self.query_length_limit = 3999 if self.tone not in "balanced" else 1999 # Limits provided by Bing model

            model_tone_selector = f"""
            return document.querySelector('cib-serp').shadowRoot
            .querySelector('cib-conversation').shadowRoot
            .querySelector('cib-welcome-container').shadowRoot
            .querySelector('cib-tone-selector').shadowRoot
            .querySelector('button.tone-{self.tone}')
            """
            self.driver.execute_script(model_tone_selector).click()
            time.sleep(1.5)


    def _get_response(self):
        '''
        Get recent Response from the model. 
        '''
        sleep_time = (self.wait_time - (time.time() - self.timer_start))
        time.sleep(max(0, sleep_time))

        # Have escaped one { with another {
        bot_response_script = f"""
        var turns = document.querySelector('cib-serp').shadowRoot
        .querySelector('cib-conversation').shadowRoot
        .querySelectorAll('cib-chat-turn')[{self.limit_counter - 1}].shadowRoot
        .querySelectorAll('cib-message-group')[1].shadowRoot
        .querySelectorAll('cib-message');
        
        var texts = [];
        for (var i = 0; i < turns.length; i++) {{{{
            var shared = turns[i].shadowRoot.querySelector('cib-shared');
            if (shared) {{{{
                texts.push(shared.innerText);
            }}}}
        }}}}
        return texts;"""
        try:
            response = "\n".join(self.driver.execute_script(bot_response_script)).strip()
            return response
        
        except: return "Unable to get response. Try increasing the wait 'delay' or Force Reload Bing"
    

    def _send_data(self,text, stream = False):
        """
        Send the data to the client. We use SHIFT+ENTER because "\n" is considered as a new line by the client
            args:
                element: Element where we want to send the data
                text: Text string
                stream: Whether to send one character at a time or in bulk. If send in bulk, "\n" is converted to " " and a chunk of 1000 words is sent
        """
        if stream:
            for character in text:
                if character == "\n":
                    self.chat_box.send_keys(Keys.SHIFT + Keys.ENTER) # Send SHIFT + ENTER
                else:
                    self.chat_box.send_keys(character) # Send the character
        
        else:
            text = text.replace("\n", " ")
            for i in range(0, len(text), 1000): # More than 1200 length is not acceptable by the model at once
                chunk = text[i:i+1000]
                self.chat_box.send_keys(chunk)
        
        self.chat_box.send_keys(Keys.ENTER)


    def chat(self, query:str, tone:str = "precise", stream = False):
        '''
        Chat with the Bing Agent. It supports only 1250 Characters. Rest of it will be trimmed
        args:
            query: Your Query moxed with prompt
            tone: Tone of the model. One of ['precise', 'balanced', 'creative']
            stream: Whether to send the whole data at once or human like one character at a time
        '''
        query = query.strip()
        self._change_tone(tone)
        
        if self.limit_counter >= 5:
            self._reload_bing_chat(self.tone) # Reload the Chat again. Previous messages will be deleted and limit_cunter will be set to 0

        if self.total_interactions > 0:
            sleep_time = (self.wait_time - (time.time() - self.timer_start)) # How many seconds have it been since last interaction
            time.sleep(max(0, sleep_time))  # Wait accordingly # If timer is remaining, then wait for some time else proceed

        self.chat_box.clear()
        time.sleep(0.2)
        try:
            self._send_data(query[:self.query_length_limit], stream)
        except: return "Message sending failed. Try Force Reload Bing or increse the 'delay' to see if it help"

        time.sleep(0.5)
        self.timer_start = time.time()
        self.limit_counter += 1 # We only get 5 interactions

        response = self._get_response()
        self.chat_history.append([query,response])
        self.total_interactions += 1
        return response