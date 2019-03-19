from data import attributes, model, speeches
import helpers

def GetCorrectAnswerResponse(handler_input):
    sessionAttributes = handler_input.attributes_manager.session_attributes
    listOfPlayers = sessionAttributes[attributes.LIST_PLAYERS]
    turnOfPlayer = int(sessionAttributes[attributes.TURN_KEY])
    noOfPlayer = int(sessionAttributes[attributes.NO_PLAYERS])
    turnOfPlayer = (turnOfPlayer+1)%noOfPlayer
    counter = int(sessionAttributes[attributes.COUNTER_KEY])
    if turnOfPlayer==0:
        correctAnswer = helpers.GetCorrectAnswer(counter+1)
        counter += 2
        sessionAttributes[attributes.TURN_KEY] = 1
        sessionAttributes[attributes.COUNTER_KEY] = counter
        response_message = speeches.MYTURN_MESSAGEFORMAT.format(correctAnswer, listOfPlayers[1])
    else:
        counter += 1
        sessionAttributes[attributes.TURN_KEY] = turnOfPlayer
        sessionAttributes[attributes.COUNTER_KEY] = counter
        response_message = speeches.PLAYERSTURN_MESSAGEFORMAT.format(listOfPlayers[turnOfPlayer])
    handler_input.response_builder.speak(response_message).set_should_end_session(False)
    return handler_input.response_builder.response


def GetIncorrectAnswerResponse(handler_input):
    sessionAttributes = handler_input.attributes_manager.session_attributes
    listOfPlayers = sessionAttributes[attributes.LIST_PLAYERS]
    turnOfPlayer = int(sessionAttributes[attributes.TURN_KEY])
    counter = int(sessionAttributes[attributes.COUNTER_KEY])
    del listOfPlayers[turnOfPlayer]
    noOfPlayer = int(sessionAttributes[attributes.NO_PLAYERS])
    noOfPlayer -= 1
    sessionAttributes[attributes.NO_PLAYERS] = noOfPlayer
    if noOfPlayer==1:
        response_message = speeches.IWIN_MESSAGE
        handler_input.response_builder.speak(response_message).set_should_end_session(True)
    else:
        turnOfPlayer = turnOfPlayer%noOfPlayer
        if turnOfPlayer==0:
            correctAnswer = helpers.GetCorrectAnswer(counter+1)
            counter += 2
            sessionAttributes[attributes.TURN_KEY] = 1
            sessionAttributes[attributes.COUNTER_KEY] = counter
            response_message = "You are out. " + speeches.MYTURN_MESSAGEFORMAT.format(correctAnswer, listOfPlayers[1])
        else:
            counter += 1
            sessionAttributes[attributes.TURN_KEY] = turnOfPlayer
            sessionAttributes[attributes.COUNTER_KEY] = counter
            response_message = speeches.PLAYERSTURN_MESSAGEFORMAT.format(listOfPlayers[turnOfPlayer])
        handler_input.response_builder.speak(response_message).set_should_end_session(False)
    return handler_input.response_builder.response