import json
import logging
# import handlers

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.response_helper import (
    get_plain_text_content, get_rich_text_content)

from ask_sdk_model import ui, Response

from handlers import LaunchRequestHandler
from handlers import HelpRequestHandler
from handlers import StopAndCancelIntentHandler
from handlers import PlayIntentHandler
from handlers import GetPlayersRequestHandler
from handlers import AnswerRequestHandler
from handlers import CatchAllExceptionHandler
from handlers import RequestLogger
from handlers import ResponseLogger

sb = SkillBuilder()

# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpRequestHandler())
sb.add_request_handler(PlayIntentHandler())
sb.add_request_handler(GetPlayersRequestHandler())
sb.add_request_handler(AnswerRequestHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()