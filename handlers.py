# Request Handler classes
import logging

from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type

from data import speeches, attributes, model
import helpers
import response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("START {0}".format(type(self)))
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes[attributes.STATE_KEY] = attributes.STATE_PLAY
        handler_input.response_builder.speak(speeches.WELCOME_MESSAGE).set_should_end_session(False)
        return handler_input.response_builder.response
        
class HelpRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
        
    def handle(self, handler_input):
        handler_input.response_builder.speak(speeches.HELP_MESSAGE).set_should_end_session(False)
        return handler_input.response_builder.response

class StopAndCancelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.StopIntent")(handler_input) or is_intent_name("AMAZON.CancelIntent")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak(speeches.GOODBYE_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response

class PlayIntentHandler(AbstractRequestHandler):
    """Handler for starting game."""
    def can_handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes
        if attributes.STATE_KEY in sessionAttributes:
            return  ( is_intent_name(model.PLAY_INTENT)(handler_input)
                    and ( sessionAttributes[attributes.STATE_KEY] == attributes.STATE_PLAY ) ) or is_intent_name("AMAZON.StartOverIntent")(handler_input)
        return False

    def handle(self, handler_input):
        logger.info("START {0}".format(type(self)))
        sessionAttributes = handler_input.attributes_manager.session_attributes
        listOfPlayers = [model.FIRST_PLAYER]
        sessionAttributes[attributes.STATE_KEY] = attributes.STATE_GETPLAYERS
        sessionAttributes[attributes.NO_PLAYERS] = 1
        sessionAttributes[attributes.LIST_PLAYERS] = listOfPlayers
        sessionAttributes[attributes.COUNTER_KEY] = 0
        handler_input.response_builder.speak(speeches.GETPLAYERCOUNT_MESSAGE).set_should_end_session(False)
        return handler_input.response_builder.response

class GetPlayersRequestHandler(AbstractRequestHandler):
    """Handler for getting player names"""
    def can_handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes
        return is_intent_name(model.GETPLAYERSANDPLAY_INTENT)(handler_input) and ( sessionAttributes[attributes.STATE_KEY] == attributes.STATE_GETPLAYERS)

    def handle(self, handler_input):
        logger.info("START {0}".format(type(self)))
        sessionAttributes = handler_input.attributes_manager.session_attributes
        if sessionAttributes[attributes.NO_PLAYERS] == 1:
            noOfPlayers = int(handler_input.request_envelope.request.intent.slots.get(model.SLOT_NUMBER).value)
            if noOfPlayers <= 1:
                handler_input.response_builder.speak(speeches.PLAYERCOUNT_ERRORMESSAGE)
            else:
                sessionAttributes[attributes.NO_PLAYERS] = noOfPlayers
                handler_input.response_builder.speak(speeches.GETPLAYERTWO_MESSAGE).set_should_end_session(False)
        else:
            listOfPlayers = sessionAttributes[attributes.LIST_PLAYERS]
            nameOfPlayer = handler_input.request_envelope.request.intent.slots.get(model.SLOT_NAME).value
            listOfPlayers.append(nameOfPlayer)
            noOfPlayers = sessionAttributes[attributes.NO_PLAYERS]
            if len(listOfPlayers) == noOfPlayers:
                sessionAttributes[attributes.STATE_KEY] = attributes.STATE_RUNNING
                sessionAttributes[attributes.TURN_KEY] = 1
                sessionAttributes[attributes.COUNTER_KEY] = 2
                handler_input.response_builder.speak(speeches.STARTGAME_MESSAGEFORMAT.format(listOfPlayers[1])).set_should_end_session(False)
            else:
                handler_input.response_builder.speak(speeches.GETPLAYERN_MESSAGE).set_should_end_session(False)
            
        return handler_input.response_builder.response

class AnswerRequestHandler(AbstractRequestHandler):
    """Handler for answers"""
    def can_handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes
        return is_intent_name(model.GETPLAYERSANDPLAY_INTENT)(handler_input) and ( sessionAttributes[attributes.STATE_KEY] == attributes.STATE_RUNNING)

    def handle(self, handler_input):
        logger.info("START {0}".format(type(self)))

        sessionAttributes = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots

        if slots.get(model.SLOT_NUMBER).value is not None:
            answer = slots.get(model.SLOT_NUMBER).value
        elif slots.get(model.SLOT_ACTION).value is not None:
            answer = slots.get(model.SLOT_ACTION).value
        else:
            handler_input.response_builder.speak(speeches.ANSWERERROR_MESSAGE).set_should_end_session(False)
            return handler_input.response_builder.response

        correctAnswer = helpers.GetCorrectAnswer(sessionAttributes[attributes.COUNTER_KEY])

        if str(correctAnswer) == str(answer):
            return response.GetCorrectAnswerResponse(handler_input)
        else:
            return response.GetIncorrectAnswerResponse(handler_input)

# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.
    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))