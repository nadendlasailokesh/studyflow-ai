from src.ai.providers.gemini import GeminiProvider
from src.ai.providers.groq import GroqProvider
from src.ai.providers.openrouter import OpenRouterProvider


class AIClient:

    def __init__(self):

        self.providers = []

        # Initialize available providers
        try:
            self.providers.append(
                ("Gemini", GeminiProvider())
            )
        except RuntimeError:
            pass

        try:
            self.providers.append(
                ("Groq", GroqProvider())
            )
        except RuntimeError:
            pass

        try:
            self.providers.append(
                ("OpenRouter", OpenRouterProvider())
            )
        except RuntimeError:
            pass


    def generate(self, prompt):

        if not self.providers:

            raise RuntimeError(
                "No AI providers are configured."
            )

        errors = []


        for name, provider in self.providers:

            try:

                print(
                    f"Trying AI provider: {name}"
                )

                result = provider.generate(
                    prompt
                )

                if result:

                    print(
                        f"AI provider used: {name}"
                    )

                    return result

            except Exception as error:

                print(
                    f"{name} failed: {error}"
                )

                errors.append(
                    f"{name}: {error}"
                )


        raise RuntimeError(
            "All AI providers failed:\n"
            + "\n".join(errors)
        )


ai_client = AIClient()