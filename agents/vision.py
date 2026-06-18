"""VisionAgent — image understanding (screenshots, diagrams, UI mockups)."""

from agents.core import DEFAULT_VISION_MODEL, ModelManager, OllamaClient, run_agent_loop
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR, read_image_b64

VISION_SYSTEM_PROMPT = (
    "Sen 'free vision' ajanisin. Sana verilen goruntuyu (ekran goruntusu, diyagram, "
    "UI mockup) analiz edip kullanicinin sorusunu yanitlarsin. Gerekirse bulgularini "
    "write_file ile workspace/ icine bir rapor olarak kaydedebilirsin, ama varsayilan "
    "olarak dogrudan metin yaniti ver."
)


class VisionAgent:
    def __init__(self, model: str = DEFAULT_VISION_MODEL, client: OllamaClient | None = None):
        self.model = model
        self.client = client or OllamaClient()
        self.manager = ModelManager(self.client)

    def run(self, prompt: str, image_path: str) -> str:
        self.manager.ensure_loaded(self.model)
        image_b64 = read_image_b64(image_path)
        messages = [
            {"role": "system", "content": VISION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt, "images": [image_b64]},
        ]
        return run_agent_loop(
            self.client,
            self.model,
            messages,
            tools_schema=FILE_TOOLS_SCHEMA,
            tool_executor=TOOL_EXECUTOR,
        )
