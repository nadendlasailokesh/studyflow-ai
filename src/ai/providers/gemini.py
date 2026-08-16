import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class GeminiProvider:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-2.5-flash"


    def generate(
        self,
        prompt,
        json_mode=False,
        response_schema=None,
    ):

        # ====================================================
        # NORMAL TEXT GENERATION
        # ====================================================

        if not json_mode:

            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
            )

            return response.text


        # ====================================================
        # STRUCTURED JSON GENERATION
        # ====================================================

        config_kwargs = {

            "response_mime_type":
                "application/json",

            "max_output_tokens":
                12000,
        }


        if response_schema is not None:

            config_kwargs[
                "response_schema"
            ] = response_schema


        config = types.GenerateContentConfig(
            **config_kwargs
        )


        response = (
            self.client.models.generate_content(

                model=self.model,

                contents=prompt,

                config=config,
            )
        )


        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )


        return response.text