DELIMITER = "_"
ACTION_SAMPLE = "Sample"
ACTION_CHECK = "Check"
ACTION_MOVE = "Move"

OBS_NULL = "-"

def parseAction(action):
    return action.split(DELIMITER)
