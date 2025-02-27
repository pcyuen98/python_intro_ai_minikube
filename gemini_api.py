import google.generativeai as genai
import time
import os
import traceback
from http_log_4_ai import HTTPLog4AI
from jsonpickle.backend import json
import web
import datetime
from attr import dataclass
from typing import Optional
import jsonpickle

@dataclass
class FeedbackResponse:
    question: str= ""
    answer : [] = None
    node_name: str = os.environ.get('NODE_NAME')
    isValidApplicationSuggestion: Optional[bool] = None  # Use Optional for nullable fields
    isHarmful: Optional[bool] = None
    harmfulType: str = ""
    total_ask: int = 0
    is_title_an_english_language: str =""
    daily_count: int = 0
    
    
class GeminiAPIKube:
    total_ask = []
    daily_count = {}
    api_key = os.environ.get('GOOGLE_API_KEY')
    total_ask_user = int(os.environ.get('TOTAL_ASK_USER'))
    node_name = os.environ.get('NODE_NAME')


    @staticmethod
    def is_json(json_string):
        """Checks if a string is valid JSON.
        
        Args:
            json_string: The string to check.
        
        Returns:
            True if the string is valid JSON, False otherwise.
        """
        try:
            json.loads(json_string)  # Attempt to parse the string as JSON
            return True  # If parsing succeeds, it's valid JSON
        except :
            return False  # If parsing fails, it's not valid JSON
        
    @staticmethod
    def add_timestamp(data_list, max_age=10):
        """Adds a timestamp to the list and removes items older than `max_age` seconds.

        Args:
            data_list: A list of data items or timestamps.
            max_age: Maximum age of items in the list in seconds (default is 10).

        Returns:
            A new list containing the timestamps (updated with the new timestamp).
        """

        current_time = datetime.datetime.now()
        new_timestamped_list = []

        # Add the new timestamp
        new_timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
        new_timestamped_list.append(new_timestamp)

        # Filter existing timestamps, keeping only those within max_age
        filtered_timestamps = [timestamp for timestamp in data_list if (
            current_time - datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        ).total_seconds() <= max_age]

        # Combine the new timestamp with the filtered existing ones
        new_timestamped_list.extend(filtered_timestamps)

        #print('New timestamped list:', new_timestamped_list)
        return new_timestamped_list
    
    @staticmethod
    def fix_data(data):
        
        data = data.replace('```json', '')
        data = data.replace('```', '')

        return data

    @staticmethod
    def ask_anything(ques):
        
        model = GeminiAPIKube.getAIKey()
        count = 0
        while True:
            try:
                count += 1
                if count >= 5:
                    raise  web.InternalError(json.dumps({"message": "AI Error Processing"})) 
                    break 
                response = model.generate_content(ques)
                response_json = str(response.text)
                
                response_json = GeminiAPIKube.fix_data(response_json)
                try:
                    if GeminiAPIKube.is_json(response_json):
                        response_json = json.loads(response_json)
                        if "py/object" in response_json:  # Check if the key exists (important!)
                            del response_json["py/object"]  # Remove the "py/object" key
                        response_json = json.dumps(response_json, indent=4)
                        feedbackResponse = FeedbackResponse(**json.loads(response_json))
                        
                        daily_count = next(iter(GeminiAPIKube.daily_count.values()), None)
                        feedbackResponse.daily_count = daily_count
                        response_json = jsonpickle.encode(feedbackResponse, indent=4)
                        break
                except Exception as error:
                    HTTPLog4AI.print_log (traceback.format_exc())
                    HTTPLog4AI.print_log ('Ask AI Parsing Response Error -->' + str(error) + ' response=' + str(response_json))
                    GeminiAPIKube.check_quota()

            except Exception as error:
                #model = Gemini.getAIKey()
                #Log4News.log(str(ques) + " gemini ask  " + str( traceback.format_exc()))
                HTTPLog4AI.print_log(" ask An exception occurred:" + str(error))
                HTTPLog4AI.print_log (traceback.format_exc())
                time.sleep(3)
        return response_json
        
    @staticmethod
    def ask_feedback(ques):
        
        model = GeminiAPIKube.getAIKey()
        count = 0
        while True:
            try:
                count += 1
                if count >= 5:
                    raise  web.InternalError(json.dumps({"message": "AI Error Processing"}))                     
                    break 
                HTTPLog4AI.print_log ('ques-->' + ques)
                response = model.generate_content(ques)
                HTTPLog4AI.print_log ('response.text-->' + response.text)
                response_json = str(response.text)
                
                response_json = GeminiAPIKube.fix_data(response_json)
                try:
                    response_json = json.loads(response_json)  # Parse the JSON string into a Python dictionary

                    if "py/object" in response_json:  # Check if the key exists (important!)
                        del response_json["py/object"]  # Remove the "py/object" key

                    response_json = json.dumps(response_json, indent=4) # Convert back to JSON
                    feedbackResponse = FeedbackResponse(**json.loads(response_json))
                    feedbackResponse.total_ask = len(GeminiAPIKube.total_ask)
                    
                    #GeminiAPIKube.update_daily_count()
                    daily_count = next(iter(GeminiAPIKube.daily_count.values()), None)
                    feedbackResponse.daily_count = daily_count
                    #print ('after asked daily count-->', daily_count)
                    
                    response_json = jsonpickle.encode(feedbackResponse, indent=4)
                    break
                except Exception as error:
                    GeminiAPIKube.check_quota()
                    HTTPLog4AI.print_log (traceback.format_exc())
                    HTTPLog4AI.print_log ('Ask AI Parsing Response Error -->' + str(error) + ' response=' + str(response_json))
            except Exception as error:
                #model = Gemini.getAIKey()
                #Log4News.log(str(ques) + " gemini ask  " + str( traceback.format_exc()))
                HTTPLog4AI.print_log(" ask An exception occurred:" + str(error))
                HTTPLog4AI.print_log (traceback.format_exc())
                time.sleep(3)
        return response_json

    @staticmethod
    def getAIKey():
        
        genai.configure(api_key=GeminiAPIKube.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model

    @staticmethod
    def update_daily_count():
        from datetime import datetime
        """Updates the count for today's date and removes old entries."""
        today = datetime.today().strftime("%Y-%m-%d")

        # Remove outdated entries (keep only today's date)
        GeminiAPIKube.daily_count = {today: GeminiAPIKube.daily_count.get(today, 0) + 1}
        
    @staticmethod
    def check_quota():
        total_user = len(GeminiAPIKube.total_ask)
        GeminiAPIKube.total_ask = GeminiAPIKube.add_timestamp(GeminiAPIKube.total_ask, 20)
        
        GeminiAPIKube.update_daily_count()
        daily_count = next(iter(GeminiAPIKube.daily_count.values()), None)
        
        if daily_count is not None and daily_count > 1000:
            HTTPLog4AI.print_log ('daily_count-->'  + str(daily_count) )
            raise  web.notfound (json.dumps({"message": "daily quota exceeded"})) # 404
        if total_user >= GeminiAPIKube.total_ask_user:
            raise  web.notfound (json.dumps({"message": "Too many requests"})) # 404
            
if __name__ == '__main__':
    feedbackResponse = FeedbackResponse()
    feedbackResponse.answer = "test"
    feedbackResponse.question = "quest"
    json_string_pretty = jsonpickle.encode(feedbackResponse, indent=4)
    feedbackResponse = jsonpickle.encode(feedbackResponse)
    print (json_string_pretty)
    