import requests


_SPARK_LLM_URL = 'http://localhost:8000'


class Api(object):
    def __init__(self, base_url, headers={}):
        self.base_url = base_url
        self.headers = headers
    
    def add_header(self, key, value):
        self.headers[key] = value
    
    def remove_header(self, key):
        del self.headers[key]
    
    def get(self, url, params):
        url = self.base_url + url
        return requests.get(url, headers=self.headers, params=params)
    
    def post(self, url, data):
        url = self.base_url + url
        return requests.post(url, headers=self.headers, json=data)


class SparkLLM(object):
    def __init__(self, session_id):
        self.api = Api(_SPARK_LLM_URL, headers={
            'Authorization': f'Bearer {session_id}', 
            'Content-Type': 'application/json'
        })
    
    def chat(self, message):
        response = self.api.post('/v1/chat/completions', data={
            'model': 'spark',
            'messages': [{'role': 'user', 'content': message}],
            'stream': False,
        }).json()
        return response['choices'][0]['message']['content']


class QWenLLM(object):
    def __init__(self, session_id):
        self.api = Api(_SPARK_LLM_URL, headers={
            'Authorization': f'Bearer {session_id}',
            'Content-Type': 'application/json'
        })
        
    def chat(self, message):
        response = self.api.post('/v1/chat/completions', data={
            'model': 'qwen',
            'messages': [{'role': 'user', 'content': message}],
            'stream': False,
        }).json()
        return response['choices'][0]['message']['content']


class KIMILLM(object):
    def __init__(self, refresh_token):
        self.api = Api(_SPARK_LLM_URL, headers={
            'Authorization': f'Bearer {refresh_token}',
            'Content-Type': 'application/json'
        })
        
    def chat(self, message):
        response = self.api.post('/v1/chat/completions', data={
            'model': 'kimi',
            'messages': [{'role': 'user', 'content': message}],
            'stream': False,
        }).json()
        return response['choices'][0]['message']['content']


class GLM(object):
    def __init__(self, refresh_token):
        self.api = Api(_SPARK_LLM_URL, headers={
            'Authorization': f'Bearer {refresh_token}',
            'Content-Type': 'application/json'
        })
    
    def chat(self, message):
        response = self.api.post('/v1/chat/completions', data={
            'model': 'glm',
            'messages': [{'role': 'user', 'content': message}],
            'stream': False,
        }).json()
        return response['choices'][0]['message']['content']


class CustomLLM(object):
    def __init__(self, name, refresh_token):
        self.name = name
        self.api = Api(_SPARK_LLM_URL, headers={
            'Authorization': f'Bearer {refresh_token}',
            'Content-Type': 'application/json'
        })
        
    def chat(self, message):
        response = self.api.post('/v1/chat/completions', data={
            'model': self.name,
            'messages': [{'role': 'user', 'content': message}],
            'stream': False,
        }).json()
        return response['choices'][0]['message']['content']


if __name__ == '__main__':
    agent = SparkLLM('9b69cb2b-fa11-47bf-9daf-4d0e359cfdb2')
    result = agent.chat('Hello, how are you?')    
    print(result)
