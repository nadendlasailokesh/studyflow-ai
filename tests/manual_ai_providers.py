from src.ai.providers.gemini import GeminiProvider
from src.ai.providers.groq import GroqProvider
from src.ai.providers.openrouter import OpenRouterProvider


PROMPT = (
    "Explain data mining in one sentence."
)


def test_gemini():

    provider = GeminiProvider()

    response = provider.generate(
        PROMPT
    )

    print("\nGemini:")
    print(response)


def test_groq():

    provider = GroqProvider()

    response = provider.generate(
        PROMPT
    )

    print("\nGroq:")
    print(response)


def test_openrouter():

    provider = OpenRouterProvider()

    response = provider.generate(
        PROMPT
    )

    print("\nOpenRouter:")
    print(response)


if __name__ == "__main__":

    test_gemini()

    test_groq()

    test_openrouter()