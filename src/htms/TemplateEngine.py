import re


class TemplateEngine:
    def __init__(self):
        self.variables = {}

    def set_variable(self, name, value):
        """Store a variable in the template engine."""
        self.variables[name] = value

    def replace_variables(self, text: str):
        """Replace placeholders in the text with corresponding variable values."""
        pattern = r"\{\{(.+?)\}\}"

        def replacer(match):
            var_name = match.group(1).strip()
            return self.variables.get(var_name, match.group(0))

        return re.sub(pattern, replacer, text)
