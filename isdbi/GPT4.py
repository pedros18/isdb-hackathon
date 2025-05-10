###############################################################
### Documentation URL: https://documentation.ubilityai.com 	###
### GitHub Repository URL: https://github.com/Ubility-SDK 	###

###################
#    Libraries    #
###################

from ubility_sdk.langchain_connectors.langchain_conversation_chain import *
from ubility_sdk.tools import *

####################
# Global Variables #
####################

globalList = []
ChatbotQuestion = 'Hello!'
ChatbotResponse = 'response'

globalList = ['ChatbotQuestion', 'ChatbotResponse']
Output = {}

###################
#    Functions    #
###################

LANGCHAIN_CONVERSATION_CHAIN_CONTENT_JSON_2 = {'query': '${ChatbotQuestion}'}
LANGCHAIN_CONVERSATION_CHAIN_PARAMS_2 = {}
LANGCHAIN_CONVERSATION_CHAIN_MODEL_2 = {'model': 'chatgpt-4o-latest', 'params': {'optionals': {'base_url': 'https://api.openai.com/v1', 'max_retries': 2, 'max_tokens': 4096, 'temperature': 0.8, 'timeout': 60000}}, 'provider': 'openAi'}
LANGCHAIN_CONVERSATION_CHAIN_MEMORY_2 = {'context': [], 'historyId': 'fd221633-e150-4da8-99ab-81fe0deb9313', 'type': 'ConversationBufferMemory'}
LANGCHAIN_CONVERSATION_CHAIN_LANGCHAINCRED_2 = '{"OpenAI": {"apiKey": ""}}'

ConversationChain1 = langchain_invoke_conversation(parseDynamicVars(LANGCHAIN_CONVERSATION_CHAIN_CONTENT_JSON_2, globalList, globals()), parseDynamicVars(LANGCHAIN_CONVERSATION_CHAIN_MODEL_2, globalList, globals()), parseDynamicVars(LANGCHAIN_CONVERSATION_CHAIN_LANGCHAINCRED_2, globalList, globals()), parseDynamicVars(LANGCHAIN_CONVERSATION_CHAIN_MEMORY_2, globalList, globals()), parseDynamicVars(LANGCHAIN_CONVERSATION_CHAIN_PARAMS_2, globalList, globals()))
Output['ConversationChain1'] = ConversationChain1
response = ConversationChain1
globalList.append('response')




print(Output)