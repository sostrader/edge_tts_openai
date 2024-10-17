from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import edge_tts
import tempfile
from fastapi.responses import StreamingResponse
from io import BytesIO
import uvicorn
from fast_langdetect import detect

app = FastAPI()

# Definir mapeamento de vozes por idioma
voice_mapping = {
    "en": {  # English (British)
        "alloy": "en-GB-RyanNeural",
        "echo": "en-GB-LibbyNeural",
        "fable": "en-GB-SoniaNeural",
        "onyx": "en-GB-ElliotNeural",
        "nova": "en-GB-MaisieNeural",
        "shimmer": "en-GB-AbbieNeural",
    },
    "pt": {  # Portuguese (Brazil)
        "alloy": "pt-BR-AntonioNeural",
        "echo": "pt-BR-FranciscaNeural",
        "fable": "pt-BR-ThalitaNeural",
        "onyx": "pt-BR-AntonioNeural",
        "nova": "pt-BR-FranciscaNeural",
        "shimmer": "pt-BR-ThalitaNeural",
    },
    "es": {  # Spanish (Spain)
        "alloy": "es-ES-AlvaroNeural",
        "echo": "es-ES-ElviraNeural",
        "fable": "es-ES-LuciaNeural",
        "onyx": "es-ES-GonzaloNeural",
        "nova": "es-ES-SergioNeural",
        "shimmer": "es-ES-PilarNeural",
    },
    "fr": {  # French (France)
        "alloy": "fr-FR-DenisNeural",
        "echo": "fr-FR-HenriNeural",
        "fable": "fr-FR-CelesteNeural",
        "onyx": "fr-FR-YannNeural",
        "nova": "fr-FR-BrigitteNeural",
        "shimmer": "fr-FR-EloiseNeural",
    },
    "it": {  # Italian (Italy)
        "alloy": "it-IT-DiegoNeural",
        "echo": "it-IT-FabianaNeural",
        "fable": "it-IT-GiorgioNeural",
        "onyx": "it-IT-IsabellaNeural",
        "nova": "it-IT-LuciaNeural",
        "shimmer": "it-IT-BiancaNeural",
    },
    "de": {  # German (Germany)
        "alloy": "de-DE-ConradNeural",
        "echo": "de-DE-KatjaNeural",
        "fable": "de-DE-AmalaNeural",
        "onyx": "de-DE-BerndNeural",
        "nova": "de-DE-ElkeNeural",
        "shimmer": "de-DE-KasperNeural",
    },
    "nl": {  # Dutch (Netherlands)
        "alloy": "nl-NL-ColetteNeural",
        "echo": "nl-NL-FennaNeural",
        "fable": "nl-NL-MaartenNeural",
        "onyx": "nl-NL-DaanNeural",
        "nova": "nl-NL-LotteNeural",
        "shimmer": "nl-NL-SofieNeural",
    },
    "ru": {  # Russian (Russia)
        "alloy": "ru-RU-DmitryNeural",
        "echo": "ru-RU-SvetlanaNeural",
        "fable": "ru-RU-DariyaNeural",
        "onyx": "ru-RU-PavelNeural",
        "nova": "ru-RU-TatyanaNeural",
        "shimmer": "ru-RU-YuriNeural",
    },
    "zh": {  # Chinese (Simplified)
        "alloy": "zh-CN-XiaochenNeural",
        "echo": "zh-CN-XiaohanNeural",
        "fable": "zh-CN-YunxiNeural",
        "onyx": "zh-CN-YunyeNeural",
        "nova": "zh-CN-XiaoxiaoNeural",
        "shimmer": "zh-CN-XiaomengNeural",
    },
    "ja": {  # Japanese
        "alloy": "ja-JP-KeitaNeural",
        "echo": "ja-JP-AyumiNeural",
        "fable": "ja-JP-NanamiNeural",
        "onyx": "ja-JP-ShioriNeural",
        "nova": "ja-JP-HarukaNeural",
        "shimmer": "ja-JP-KazukiNeural",
    },
    "ko": {  # Korean
        "alloy": "ko-KR-SebinNeural",
        "echo": "ko-KR-InjiNeural",
        "fable": "ko-KR-GenaNeural",
        "onyx": "ko-KR-HyunjunNeural",
        "nova": "ko-KR-HyeriNeural",
        "shimmer": "ko-KR-SoyiNeural",
    },
    "ar": {  # Arabic
        "alloy": "ar-SA-HamedNeural",
        "echo": "ar-SA-ZariyahNeural",
        "fable": "ar-SA-MonaNeural",
        "onyx": "ar-SA-FahedNeural",
        "nova": "ar-SA-SalmaNeural",
        "shimmer": "ar-SA-IbrahimNeural",
    }
}

def get_first_line(input_text: str) -> str:
    first_line = input_text.split("\n", 1)[0].strip()  # Pega a primeira linha e remove espaços
    if first_line.startswith("##"):
        first_line = first_line.lstrip("#").strip()  # Remove os '#' do início
    return first_line

# Definir modelo de entrada para TTS
class TTSRequest(BaseModel):
    input: str
    voice: str

# Função para geração de fala a partir do texto
async def text_to_speech(input_text, voice_short_name):
    communicate = edge_tts.Communicate(input_text, voice_short_name)
    
    # Usar tempfile para salvar o áudio temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_path = tmp_file.name
        await communicate.save(tmp_path)
    
    return tmp_path

# Endpoint para converter texto em fala
@app.post("/v1/audio/speech")
async def generate_speech(request: TTSRequest):
    if not request.input.strip():
        raise HTTPException(status_code=400, detail="Texto não pode estar vazio.")
    if request.voice not in voice_mapping["en"]:
        raise HTTPException(status_code=400, detail="A chave de voz não é válida.")
    
    # Detectar idioma
    first_line = get_first_line(request.input)
    detected_lang = detect(first_line)["lang"]
    
    if detected_lang not in voice_mapping:
        raise HTTPException(status_code=400, detail="Idioma não suportado.")
    
    # Selecionar voz com base no idioma
    selected_voice = voice_mapping[detected_lang][request.voice]
    
    # Gerar o arquivo de áudio
    audio_path = await text_to_speech(request.input.lstrip("#").strip(), selected_voice)
    
    # Retornar o arquivo de áudio como streaming
    with open(audio_path, "rb") as audio_file:
        audio_bytes = BytesIO(audio_file.read())
        audio_bytes.seek(0)
        
        headers = {
            "x-generated-voice": selected_voice,
        }
        
        return StreamingResponse(audio_bytes, media_type="audio/mpeg", headers=headers)

# Executar o servidor se o script for executado diretamente
if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    uvicorn.run(app, host=host, port=port)
