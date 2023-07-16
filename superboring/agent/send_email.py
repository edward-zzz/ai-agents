from .base import BaseAgent


class SendEmailAgent(BaseAgent):
    @property
    def function_specs(self):
        return {
            "name": "send_email",
            "description": "Send email for user",
            "parameters": {
                "type": "object",
                "properties": {
                    "receiver_email_address": {
                        "type": "string",
                        "description": "The email address of receiver, ask the user to get the email address",
                    },
                    "email_title": {
                        "type": "string",
                        "description": "The title of email, ask the user to get the email title",
                    },
                },
                "required": [
                    "receiver_address",
                    "email_title",
                ],
            },
        }

    def run(self, args):
        return f"An email with title[{args['email_title']}] has been sent to {args['receiver_email_address']} successfully!"
    