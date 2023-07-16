from .base import BaseAgent


class ChangeTimezoneAgent(BaseAgent):
    @property
    def function_specs(self):
        return {
            "name": "change_timezone",
            "description": "Help user to change timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_timezone": {
                        "type": "string",
                        "description": "The target timezone the user want to switch to, ask the user to get the target timezone",
                    },
                },
                "required": [
                    "target_timezone",
                ],
            },
        }

    def run(self, args):
        return f"Switched your timezone to {args['target_timezone']} successfully!"
