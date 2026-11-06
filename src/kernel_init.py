import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# Initialize Semantic Kernel
def init_kernel():
    # Use Azure OpenAI or OpenAI if env vars are set; otherwise use dummy local model.
    api_key = os.getenv("OPENAI_API_KEY")
    org = os.getenv("OPENAI_ORG_ID")
    if api_key:
        kernel = Kernel()
        # Using GPT-3.5 Turbo as default for demo; replace with desired model.
        kernel.add_chat_service(
            "chat-gpt",
            OpenAIChatCompletion(
                model_id="gpt-3.5-turbo",
                api_key=api_key,
                org_id=org,
            ),
        )
    else:
        # Fallback: no LLM – kernel does nothing but provides the interface.
        kernel = Kernel()
    return kernel
