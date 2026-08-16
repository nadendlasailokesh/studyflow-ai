from src.ai.providers.gemini import GeminiProvider
from src.ai.providers.groq import GroqProvider
from src.ai.providers.openrouter import OpenRouterProvider


class AIClient:

    def __init__(self):

        self.providers = []

        # ====================================================
        # INITIALIZE AVAILABLE PROVIDERS
        # ====================================================

        try:

            self.providers.append(
                ("Gemini", GeminiProvider())
            )

        except Exception as error:

            print(
                f"Gemini unavailable: {error}"
            )


        try:

            self.providers.append(
                ("Groq", GroqProvider())
            )

        except Exception as error:

            print(
                f"Groq unavailable: {error}"
            )


        try:

            self.providers.append(
                ("OpenRouter", OpenRouterProvider())
            )

        except Exception as error:

            print(
                f"OpenRouter unavailable: {error}"
            )


        # ====================================================
        # STARTUP INFORMATION
        # ====================================================

        if self.providers:

            print(
                "Available AI providers: "
                + ", ".join(
                    name
                    for name, _ in self.providers
                )
            )

        else:

            print(
                "WARNING: No AI providers are configured."
            )


    # ========================================================
    # GENERATE AI RESPONSE
    # ========================================================

    def generate(
        self,
        prompt
    ):

        if not self.providers:

            raise RuntimeError(
                "No AI providers are configured. "
                "Check your API keys and provider configuration."
            )


        errors = []


        # ====================================================
        # TRY PROVIDERS IN ORDER
        # ====================================================

        for name, provider in self.providers:

            print(
                f"\nTrying AI provider: {name}..."
            )


            try:

                result = provider.generate(
                    prompt
                )


                # ------------------------------------------------
                # Validate response
                # ------------------------------------------------

                if result is None:

                    raise RuntimeError(
                        "Provider returned None."
                    )


                result = str(
                    result
                ).strip()


                if not result:

                    raise RuntimeError(
                        "Provider returned an empty response."
                    )


                # ------------------------------------------------
                # SUCCESS
                # ------------------------------------------------

                print(
                    f"AI provider used: {name}"
                )


                return result


            except Exception as error:

                error_message = str(
                    error
                )


                print(
                    f"{name} failed: "
                    f"{error_message}"
                )


                errors.append(
                    f"{name}: {error_message}"
                )


        # ====================================================
        # ALL PROVIDERS FAILED
        # ====================================================

        raise RuntimeError(
            "All configured AI providers failed.\n\n"
            + "\n".join(errors)
        )
        # ========================================================
    # GENERATE JSON RESPONSE
    # ========================================================

    def generate_json(
        self,
        prompt,
        response_schema=None,
    ):
        """
        Generate a JSON response.

        Providers that support structured JSON generation
        can use their native JSON mode.

        Providers that do not support it fall back to
        normal generation so the existing repair/validation
        pipeline can handle the response.
        """

        if not self.providers:

            raise RuntimeError(
                "No AI providers are configured. "
                "Check your API keys and provider configuration."
            )


        errors = []


        for name, provider in self.providers:

            print(
                f"\nTrying JSON AI provider: {name}..."
            )


            try:

                # ------------------------------------------------
                # Gemini
                # ------------------------------------------------

                if name == "Gemini":

                    result = provider.generate(

                        prompt,

                        json_mode=True,

                        response_schema=response_schema,

                    )
                # ------------------------------------------------
                # Other providers
                #
                # They continue using normal generation.
                # The syllabus validator will check the result.
                # ------------------------------------------------

                else:

                    result = provider.generate(
                        prompt
                    )


                # ------------------------------------------------
                # Validate basic response
                # ------------------------------------------------

                if result is None:

                    raise RuntimeError(
                        "Provider returned None."
                    )


                result = str(
                    result
                ).strip()


                if not result:

                    raise RuntimeError(
                        "Provider returned an empty response."
                    )


                print(
                    f"AI JSON provider used: {name}"
                )


                return result


            except Exception as error:

                error_message = str(
                    error
                )


                print(
                    f"{name} JSON generation failed: "
                    f"{error_message}"
                )


                errors.append(
                    f"{name}: {error_message}"
                )


        raise RuntimeError(
            "All configured AI providers failed "
            "during JSON generation.\n\n"
            + "\n".join(errors)
        )

# ============================================================
# GLOBAL CLIENT
# ============================================================

ai_client = AIClient()