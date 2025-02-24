import web
import os
import sys
import random
from http_log_4_ai import HTTPLog4AI
from jsonpickle.backend import json
import jsonpickle
from gemini_api import GeminiAPIKube, FeedbackResponse

URLS = (
    '/mini/api/chat/feedback', 'HTTPPostChatFeedback',
    '/mini/api/chat', 'HTTPPostChatGeneral',
    '/mini', 'Chat_Test',
    '/', 'Chat_Test',
)

class Chat_Test(object):

    def GET(self):
        api_key = os.environ.get('GOOGLE_API_KEY')
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('strict-origin-when-cross-origin', 'true')
        GeminiAPIKube.check_quota()
        
        year = random.randint(1900, 2000)  # Generate the random year *outside* the string
        ques = f"anything special in {year}"  # Use f-string formatting (cleaner)
        total_user = len(GeminiAPIKube.total_ask)
        feedbackResponse = FeedbackResponse()
        feedbackResponse.total_ask = total_user
        feedbackResponse.question = ques
        feedbackResponse = jsonpickle.encode(feedbackResponse, indent=4)
        
        header = 'fill in the blank, do not change the json elements and return in this json format only for python processing. '
        response_json = GeminiAPIKube.ask_anything(header + feedbackResponse)

        HTTPLog4AI.print_log ('chat_test-->' + str(api_key) )
        return response_json

class HTTPPostChatGeneral(object):
    
    def POST(self):
        
        web.header('Access-Control-Allow-Origin','*')
        web.header('Access-Control-Allow-Methods', 'content-type');
        
        total_user = len(GeminiAPIKube.total_ask)

        HTTPLog4AI.print_log('HTTPPostChatGeneral  total user-->' + str(total_user) )
        
        GeminiAPIKube.check_quota()
            
        json_data = web.data()
        json_data = json_data.decode('utf-8') 
        
        response_json = GeminiAPIKube.ask_anything(json_data)
        
        return response_json
    
class HTTPPostChatFeedback(object):
    
    def POST(self):
        
        web.header('Access-Control-Allow-Origin','*')
        web.header('Access-Control-Allow-Methods', 'content-type');
        
        total_user = len(GeminiAPIKube.total_ask)

        HTTPLog4AI.print_log('HTTPPostChatGeneral  total user-->' + str(total_user) )
        
        GeminiAPIKube.check_quota()
            
        json_data = web.data()
        json_data = json_data.decode('utf-8') 
        
        feedbackResponse = FeedbackResponse()
        header = 'fill in the blank value. Fill in the answer value in the JSON element without special characters and double quote in the message. Do not change the json elements, fix the JSON and return a valid JSON in this JSON double quote format only for python processing. '
        feedbackResponse.question = json_data
        
        feedbackResponse = jsonpickle.encode(feedbackResponse, indent=4)
        response_json = GeminiAPIKube.ask_feedback(header + feedbackResponse)
        
        
        return json.dumps(response_json)
        
        #return jsonString
    def OPTIONS(self):
        
        web.header('Access-Control-Allow-Origin','*')
        web.header('Access-Control-Allow-Methods', 'content-type');
        print('OPTIONS starting' )
        
def main():
    """
    Main function starting app
    """
    print (sys.path)

    http_app = web.application(URLS, globals());
    os.environ["PORT"] = "8091";
    
    http_app.run()

if __name__ == "__main__":
    HTTPLog4AI.print_log ('test_ai starting v0.13' )
    main()
