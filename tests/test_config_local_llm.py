from pathlib import Path

from neuro_simulator.neuro_sama.config import Config


def test_local_openai_compatible_llm_does_not_require_api_key(tmp_path: Path):
    (tmp_path / "prompts").mkdir()
    (tmp_path / "memory").mkdir()

    config = Config(
        {
            "general": {
                "llm_services": [
                    {
                        "id": "local_ollama",
                        "name": "Local Ollama",
                        "provider": "local_openai",
                        "url": "http://127.0.0.1:11434/v1",
                        "model": "llama3.1:8b",
                        "key": "",
                    }
                ],
                "tts_services": [
                    {
                        "id": "azure_default",
                        "key": "tts-key",
                        "region": "eastus",
                        "timeout": 10,
                    }
                ],
            },
            "neuro_sama": {
                "llm_service_id": "local_ollama",
                "tts_service_id": "azure_default",
                "server_settings": {"host": "127.0.0.1", "port": 8001},
            },
        },
        str(tmp_path),
    )

    assert config.OPENAI_API_KEY == "not-needed"
    assert config.OPENAI_BASE_URL == "http://127.0.0.1:11434/v1"
    assert config.OPENAI_MODEL == "llama3.1:8b"
    assert config.LLM_PROVIDER == "local_openai"
