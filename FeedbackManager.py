class FeedbackManager:
    def __init__(self):
        self.text = ""

    def set(self, content):
        self.text = content

    def get(self):
        return self.text

feedback_manager = FeedbackManager()