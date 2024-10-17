from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import edge_tts
import tempfile
from fastapi.responses import StreamingResponse
from io import BytesIO
import uvicorn

app = FastAPI()

# Definir mapeamento de vozes (usando apenas multilíngues)
voice_mapping = {
    "default": {  # Vozes multilíngues para todos os idiomas
        "alloy": "en-US-AndrewMultilingualNeural", 
        "echo": "en-US-AvaMultilingualNeural",
        "fable": "en-US-EmmaMultilingualNeural", 
        "onyx": "en-US-BrianMultilingualNeural", 
        "nova": "fr-FR-VivienneMultilingualNeural", 
        "shimmer": "fr-FR-RemyMultilingualNeural",
    }
}


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
    if request.voice not in voice_mapping["default"]:
        raise HTTPException(status_code=400, detail="A chave de voz não é válida.")
    
    # Selecionar voz com base no idioma (agora sempre "default")
    selected_voice = voice_mapping["default"][request.voice]
    
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
    port = 80
    uvicorn.run(app, host=host, port=port) 