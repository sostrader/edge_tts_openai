from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import edge_tts
import tempfile
from fastapi.responses import StreamingResponse
from io import BytesIO
import uvicorn
from bs4 import BeautifulSoup
from markdown import markdown
import re

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
        "Thalita - pt-BR (Female)": "pt-BR-ThalitaNeural",
        "Antonio - pt-BR (Male)": "pt-BR-AntonioNeural",
        "Francisca - pt-BR (Female)": "pt-BR-FranciscaNeural",
        "Duarte - pt-PT (Male)": "pt-PT-DuarteNeural",
        "Raquel - pt-PT (Female)": "pt-PT-RaquelNeural",
        "Adri - af-ZA (Female)": "af-ZA-AdriNeural",
        "Willem - af-ZA (Male)": "af-ZA-WillemNeural",
        "Anila - sq-AL (Female)": "sq-AL-AnilaNeural",
        "Ilir - sq-AL (Male)": "sq-AL-IlirNeural",
        "Ameha - am-ET (Male)": "am-ET-AmehaNeural",
        "Mekdes - am-ET (Female)": "am-ET-MekdesNeural",
        "Amina - ar-DZ (Female)": "ar-DZ-AminaNeural",
        "Ismael - ar-DZ (Male)": "ar-DZ-IsmaelNeural",
        "Ali - ar-BH (Male)": "ar-BH-AliNeural",
        "Laila - ar-BH (Female)": "ar-BH-LailaNeural",
        "Salma - ar-EG (Female)": "ar-EG-SalmaNeural",
        "Shakir - ar-EG (Male)": "ar-EG-ShakirNeural",
        "Bassel - ar-IQ (Male)": "ar-IQ-BasselNeural",
        "Rana - ar-IQ (Female)": "ar-IQ-RanaNeural",
        "Sana - ar-JO (Female)": "ar-JO-SanaNeural",
        "Taim - ar-JO (Male)": "ar-JO-TaimNeural",
        "Fahed - ar-KW (Male)": "ar-KW-FahedNeural",
        "Noura - ar-KW (Female)": "ar-KW-NouraNeural",
        "Layla - ar-LB (Female)": "ar-LB-LaylaNeural",
        "Rami - ar-LB (Male)": "ar-LB-RamiNeural",
        "Iman - ar-LY (Female)": "ar-LY-ImanNeural",
        "Omar - ar-LY (Male)": "ar-LY-OmarNeural",
        "Jamal - ar-MA (Male)": "ar-MA-JamalNeural",
        "Mouna - ar-MA (Female)": "ar-MA-MounaNeural",
        "Abdullah - ar-OM (Male)": "ar-OM-AbdullahNeural",
        "Aysha - ar-OM (Female)": "ar-OM-AyshaNeural",
        "Amal - ar-QA (Female)": "ar-QA-AmalNeural",
        "Moaz - ar-QA (Male)": "ar-QA-MoazNeural",
        "Hamed - ar-SA (Male)": "ar-SA-HamedNeural",
        "Zariyah - ar-SA (Female)": "ar-SA-ZariyahNeural",
        "Amany - ar-SY (Female)": "ar-SY-AmanyNeural",
        "Laith - ar-SY (Male)": "ar-SY-LaithNeural",
        "Hedi - ar-TN (Male)": "ar-TN-HediNeural",
        "Reem - ar-TN (Female)": "ar-TN-ReemNeural",
        "Fatima - ar-AE (Female)": "ar-AE-FatimaNeural",
        "Hamdan - ar-AE (Male)": "ar-AE-HamdanNeural",
        "Maryam - ar-YE (Female)": "ar-YE-MaryamNeural",
        "Saleh - ar-YE (Male)": "ar-YE-SalehNeural",
        "Babek - az-AZ (Male)": "az-AZ-BabekNeural",
        "Banu - az-AZ (Female)": "az-AZ-BanuNeural",
        "Nabanita - bn-BD (Female)": "bn-BD-NabanitaNeural",
        "Pradeep - bn-BD (Male)": "bn-BD-PradeepNeural",
        "Bashkar - bn-IN (Male)": "bn-IN-BashkarNeural",
        "Tanishaa - bn-IN (Female)": "bn-IN-TanishaaNeural",
        "Goran - bs-BA (Male)": "bs-BA-GoranNeural",
        "Vesna - bs-BA (Female)": "bs-BA-VesnaNeural",
        "Borislav - bg-BG (Male)": "bg-BG-BorislavNeural",
        "Kalina - bg-BG (Female)": "bg-BG-KalinaNeural",
        "Nilar - my-MM (Female)": "my-MM-NilarNeural",
        "Thiha - my-MM (Male)": "my-MM-ThihaNeural",
        "Enric - ca-ES (Male)": "ca-ES-EnricNeural",
        "Joana - ca-ES (Female)": "ca-ES-JoanaNeural",
        "HiuGaai - zh-HK (Female)": "zh-HK-HiuGaaiNeural",
        "HiuMaan - zh-HK (Female)": "zh-HK-HiuMaanNeural",
        "WanLung - zh-HK (Male)": "zh-HK-WanLungNeural",
        "Xiaoxiao - zh-CN (Female)": "zh-CN-XiaoxiaoNeural",
        "Xiaoyi - zh-CN (Female)": "zh-CN-XiaoyiNeural",
        "Yunjian - zh-CN (Male)": "zh-CN-YunjianNeural",
        "Yunxi - zh-CN (Male)": "zh-CN-YunxiNeural",
        "Yunxia - zh-CN (Male)": "zh-CN-YunxiaNeural",
        "Yunyang - zh-CN (Male)": "zh-CN-YunyangNeural",
        "Xiaobei - zh-CN-liaoning (Female)": "zh-CN-liaoning-XiaobeiNeural",
        "HsiaoChen - zh-TW (Female)": "zh-TW-HsiaoChenNeural",
        "YunJhe - zh-TW (Male)": "zh-TW-YunJheNeural",
        "HsiaoYu - zh-TW (Female)": "zh-TW-HsiaoYuNeural",
        "Xiaoni - zh-CN-shaanxi (Female)": "zh-CN-shaanxi-XiaoniNeural",
        "Gabrijela - hr-HR (Female)": "hr-HR-GabrijelaNeural",
        "Srecko - hr-HR (Male)": "hr-HR-SreckoNeural",
        "Antonin - cs-CZ (Male)": "cs-CZ-AntoninNeural",
        "Vlasta - cs-CZ (Female)": "cs-CZ-VlastaNeural",
        "Christel - da-DK (Female)": "da-DK-ChristelNeural",
        "Jeppe - da-DK (Male)": "da-DK-JeppeNeural",
        "Arnaud - nl-BE (Male)": "nl-BE-ArnaudNeural",
        "Dena - nl-BE (Female)": "nl-BE-DenaNeural",
        "Colette - nl-NL (Female)": "nl-NL-ColetteNeural",
        "Fenna - nl-NL (Female)": "nl-NL-FennaNeural",
        "Maarten - nl-NL (Male)": "nl-NL-MaartenNeural",
        "Natasha - en-AU (Female)": "en-AU-NatashaNeural",
        "William - en-AU (Male)": "en-AU-WilliamNeural",
        "Clara - en-CA (Female)": "en-CA-ClaraNeural",
        "Liam - en-CA (Male)": "en-CA-LiamNeural",
        "Sam - en-HK (Male)": "en-HK-SamNeural",
        "Yan - en-HK (Female)": "en-HK-YanNeural",
        "NeerjaExpressive - en-IN (Female)": "en-IN-NeerjaExpressiveNeural",
        "Neerja - en-IN (Female)": "en-IN-NeerjaNeural",
        "Prabhat - en-IN (Male)": "en-IN-PrabhatNeural",
        "Connor - en-IE (Male)": "en-IE-ConnorNeural",
        "Emily - en-IE (Female)": "en-IE-EmilyNeural",
        "Asilia - en-KE (Female)": "en-KE-AsiliaNeural",
        "Chilemba - en-KE (Male)": "en-KE-ChilembaNeural",
        "Mitchell - en-NZ (Male)": "en-NZ-MitchellNeural",
        "Molly - en-NZ (Female)": "en-NZ-MollyNeural",
        "Abeo - en-NG (Male)": "en-NG-AbeoNeural",
        "Ezinne - en-NG (Female)": "en-NG-EzinneNeural",
        "James - en-PH (Male)": "en-PH-JamesNeural",
        "Rosa - en-PH (Female)": "en-PH-RosaNeural",
        "Luna - en-SG (Female)": "en-SG-LunaNeural",
        "Wayne - en-SG (Male)": "en-SG-WayneNeural",
        "Leah - en-ZA (Female)": "en-ZA-LeahNeural",
        "Luke - en-ZA (Male)": "en-ZA-LukeNeural",
        "Elimu - en-TZ (Male)": "en-TZ-ElimuNeural",
        "Imani - en-TZ (Female)": "en-TZ-ImaniNeural",
        "Libby - en-GB (Female)": "en-GB-LibbyNeural",
        "Maisie - en-GB (Female)": "en-GB-MaisieNeural",
        "Ryan - en-GB (Male)": "en-GB-RyanNeural",
        "Sonia - en-GB (Female)": "en-GB-SoniaNeural",
        "Thomas - en-GB (Male)": "en-GB-ThomasNeural",
        "AvaMultilingual - en-US (Female)": "en-US-AvaMultilingualNeural",
        "AndrewMultilingual - en-US (Male)": "en-US-AndrewMultilingualNeural",
        "EmmaMultilingual - en-US (Female)": "en-US-EmmaMultilingualNeural",
        "BrianMultilingual - en-US (Male)": "en-US-BrianMultilingualNeural",
        "Ava - en-US (Female)": "en-US-AvaNeural",
        "Andrew - en-US (Male)": "en-US-AndrewNeural",
        "Emma - en-US (Female)": "en-US-EmmaNeural",
        "Brian - en-US (Male)": "en-US-BrianNeural",
        "Ana - en-US (Female)": "en-US-AnaNeural",
        "Aria - en-US (Female)": "en-US-AriaNeural",
        "Christopher - en-US (Male)": "en-US-ChristopherNeural",
        "Eric - en-US (Male)": "en-US-EricNeural",
        "Guy - en-US (Male)": "en-US-GuyNeural",
        "Jenny - en-US (Female)": "en-US-JennyNeural",
        "Michelle - en-US (Female)": "en-US-MichelleNeural",
        "Roger - en-US (Male)": "en-US-RogerNeural",
        "Steffan - en-US (Male)": "en-US-SteffanNeural",
        "Anu - et-EE (Female)": "et-EE-AnuNeural",
        "Kert - et-EE (Male)": "et-EE-KertNeural",
        "Angelo - fil-PH (Male)": "fil-PH-AngeloNeural",
        "Blessica - fil-PH (Female)": "fil-PH-BlessicaNeural",
        "Harri - fi-FI (Male)": "fi-FI-HarriNeural",
        "Noora - fi-FI (Female)": "fi-FI-NooraNeural",
        "Charline - fr-BE (Female)": "fr-BE-CharlineNeural",
        "Gerard - fr-BE (Male)": "fr-BE-GerardNeural",
        "Thierry - fr-CA (Male)": "fr-CA-ThierryNeural",
        "Antoine - fr-CA (Male)": "fr-CA-AntoineNeural",
        "Jean - fr-CA (Male)": "fr-CA-JeanNeural",
        "Sylvie - fr-CA (Female)": "fr-CA-SylvieNeural",
        "VivienneMultilingual - fr-FR (Female)": "fr-FR-VivienneMultilingualNeural",
        "RemyMultilingual - fr-FR (Male)": "fr-FR-RemyMultilingualNeural",
        "Denise - fr-FR (Female)": "fr-FR-DeniseNeural",
        "Eloise - fr-FR (Female)": "fr-FR-EloiseNeural",
        "Henri - fr-FR (Male)": "fr-FR-HenriNeural",
        "Ariane - fr-CH (Female)": "fr-CH-ArianeNeural",
        "Fabrice - fr-CH (Male)": "fr-CH-FabriceNeural",
        "Roi - gl-ES (Male)": "gl-ES-RoiNeural",
        "Sabela - gl-ES (Female)": "gl-ES-SabelaNeural",
        "Eka - ka-GE (Female)": "ka-GE-EkaNeural",
        "Giorgi - ka-GE (Male)": "ka-GE-GiorgiNeural",
        "Ingrid - de-AT (Female)": "de-AT-IngridNeural",
        "Jonas - de-AT (Male)": "de-AT-JonasNeural",
        "SeraphinaMultilingual - de-DE (Female)": "de-DE-SeraphinaMultilingualNeural",
        "FlorianMultilingual - de-DE (Male)": "de-DE-FlorianMultilingualNeural",
        "Amala - de-DE (Female)": "de-DE-AmalaNeural",
        "Conrad - de-DE (Male)": "de-DE-ConradNeural",
        "Katja - de-DE (Female)": "de-DE-KatjaNeural",
        "Killian - de-DE (Male)": "de-DE-KillianNeural",
        "Jan - de-CH (Male)": "de-CH-JanNeural",
        "Leni - de-CH (Female)": "de-CH-LeniNeural",
        "Athina - el-GR (Female)": "el-GR-AthinaNeural",
        "Nestoras - el-GR (Male)": "el-GR-NestorasNeural",
        "Dhwani - gu-IN (Female)": "gu-IN-DhwaniNeural",
        "Niranjan - gu-IN (Male)": "gu-IN-NiranjanNeural",
        "Avri - he-IL (Male)": "he-IL-AvriNeural",
        "Hila - he-IL (Female)": "he-IL-HilaNeural",
        "Madhur - hi-IN (Male)": "hi-IN-MadhurNeural",
        "Swara - hi-IN (Female)": "hi-IN-SwaraNeural",
        "Noemi - hu-HU (Female)": "hu-HU-NoemiNeural",
        "Tamas - hu-HU (Male)": "hu-HU-TamasNeural",
        "Gudrun - is-IS (Female)": "is-IS-GudrunNeural",
        "Gunnar - is-IS (Male)": "is-IS-GunnarNeural",
        "Ardi - id-ID (Male)": "id-ID-ArdiNeural",
        "Gadis - id-ID (Female)": "id-ID-GadisNeural",
        "Colm - ga-IE (Male)": "ga-IE-ColmNeural",
        "Orla - ga-IE (Female)": "ga-IE-OrlaNeural",
        "Giuseppe - it-IT (Male)": "it-IT-GiuseppeNeural",
        "Diego - it-IT (Male)": "it-IT-DiegoNeural",
        "Elsa - it-IT (Female)": "it-IT-ElsaNeural",
        "Isabella - it-IT (Female)": "it-IT-IsabellaNeural",
        "Keita - ja-JP (Male)": "ja-JP-KeitaNeural",
        "Nanami - ja-JP (Female)": "ja-JP-NanamiNeural",
        "Dimas - jv-ID (Male)": "jv-ID-DimasNeural",
        "Siti - jv-ID (Female)": "jv-ID-SitiNeural",
        "Gagan - kn-IN (Male)": "kn-IN-GaganNeural",
        "Sapna - kn-IN (Female)": "kn-IN-SapnaNeural",
        "Aigul - kk-KZ (Female)": "kk-KZ-AigulNeural",
        "Daulet - kk-KZ (Male)": "kk-KZ-DauletNeural",
        "Piseth - km-KH (Male)": "km-KH-PisethNeural",
        "Sreymom - km-KH (Female)": "km-KH-SreymomNeural",
        "Hyunsu - ko-KR (Male)": "ko-KR-HyunsuNeural",
        "InJoon - ko-KR (Male)": "ko-KR-InJoonNeural",
        "SunHi - ko-KR (Female)": "ko-KR-SunHiNeural",
        "Chanthavong - lo-LA (Male)": "lo-LA-ChanthavongNeural",
        "Keomany - lo-LA (Female)": "lo-LA-KeomanyNeural",
        "Everita - lv-LV (Female)": "lv-LV-EveritaNeural",
        "Nils - lv-LV (Male)": "lv-LV-NilsNeural",
        "Leonas - lt-LT (Male)": "lt-LT-LeonasNeural",
        "Ona - lt-LT (Female)": "lt-LT-OnaNeural",
        "Aleksandar - mk-MK (Male)": "mk-MK-AleksandarNeural",
        "Marija - mk-MK (Female)": "mk-MK-MarijaNeural",
        "Osman - ms-MY (Male)": "ms-MY-OsmanNeural",
        "Yasmin - ms-MY (Female)": "ms-MY-YasminNeural",
        "Midhun - ml-IN (Male)": "ml-IN-MidhunNeural",
        "Sobhana - ml-IN (Female)": "ml-IN-SobhanaNeural",
        "Grace - mt-MT (Female)": "mt-MT-GraceNeural",
        "Joseph - mt-MT (Male)": "mt-MT-JosephNeural",
        "Aarohi - mr-IN (Female)": "mr-IN-AarohiNeural",
        "Manohar - mr-IN (Male)": "mr-IN-ManoharNeural",
        "Bataa - mn-MN (Male)": "mn-MN-BataaNeural",
        "Yesui - mn-MN (Female)": "mn-MN-YesuiNeural",
        "Hemkala - ne-NP (Female)": "ne-NP-HemkalaNeural",
        "Sagar - ne-NP (Male)": "ne-NP-SagarNeural",
        "Finn - nb-NO (Male)": "nb-NO-FinnNeural",
        "Pernille - nb-NO (Female)": "nb-NO-PernilleNeural",
        "GulNawaz - ps-AF (Male)": "ps-AF-GulNawazNeural",
        "Latifa - ps-AF (Female)": "ps-AF-LatifaNeural",
        "Dilara - fa-IR (Female)": "fa-IR-DilaraNeural",
        "Farid - fa-IR (Male)": "fa-IR-FaridNeural",
        "Marek - pl-PL (Male)": "pl-PL-MarekNeural",
        "Zofia - pl-PL (Female)": "pl-PL-ZofiaNeural",
        "Alina - ro-RO (Female)": "ro-RO-AlinaNeural",
        "Emil - ro-RO (Male)": "ro-RO-EmilNeural",
        "Dmitry - ru-RU (Male)": "ru-RU-DmitryNeural",
        "Svetlana - ru-RU (Female)": "ru-RU-SvetlanaNeural",
        "Nicholas - sr-RS (Male)": "sr-RS-NicholasNeural",
        "Sophie - sr-RS (Female)": "sr-RS-SophieNeural",
        "Sameera - si-LK (Male)": "si-LK-SameeraNeural",
        "Thilini - si-LK (Female)": "si-LK-ThiliniNeural",
        "Lukas - sk-SK (Male)": "sk-SK-LukasNeural",
        "Viktoria - sk-SK (Female)": "sk-SK-ViktoriaNeural",
        "Petra - sl-SI (Female)": "sl-SI-PetraNeural",
        "Rok - sl-SI (Male)": "sl-SI-RokNeural",
        "Muuse - so-SO (Male)": "so-SO-MuuseNeural",
        "Ubax - so-SO (Female)": "so-SO-UbaxNeural",
        "Elena - es-AR (Female)": "es-AR-ElenaNeural",
        "Tomas - es-AR (Male)": "es-AR-TomasNeural",
        "Marcelo - es-BO (Male)": "es-BO-MarceloNeural",
        "Sofia - es-BO (Female)": "es-BO-SofiaNeural",
        "Catalina - es-CL (Female)": "es-CL-CatalinaNeural",
        "Lorenzo - es-CL (Male)": "es-CL-LorenzoNeural",
        "Ximena - es-ES (Female)": "es-ES-XimenaNeural",
        "Gonzalo - es-CO (Male)": "es-CO-GonzaloNeural",
        "Salome - es-CO (Female)": "es-CO-SalomeNeural",
        "Juan - es-CR (Male)": "es-CR-JuanNeural",
        "Maria - es-CR (Female)": "es-CR-MariaNeural",
        "Belkys - es-CU (Female)": "es-CU-BelkysNeural",
        "Manuel - es-CU (Male)": "es-CU-ManuelNeural",
        "Emilio - es-DO (Male)": "es-DO-EmilioNeural",
        "Ramona - es-DO (Female)": "es-DO-RamonaNeural",
        "Andrea - es-EC (Female)": "es-EC-AndreaNeural",
        "Luis - es-EC (Male)": "es-EC-LuisNeural",
        "Lorena - es-SV (Female)": "es-SV-LorenaNeural",
        "Rodrigo - es-SV (Male)": "es-SV-RodrigoNeural",
        "Javier - es-GQ (Male)": "es-GQ-JavierNeural",
        "Teresa - es-GQ (Female)": "es-GQ-TeresaNeural",
        "Andres - es-GT (Male)": "es-GT-AndresNeural",
        "Marta - es-GT (Female)": "es-GT-MartaNeural",
        "Carlos - es-HN (Male)": "es-HN-CarlosNeural",
        "Karla - es-HN (Female)": "es-HN-KarlaNeural",
        "Dalia - es-MX (Female)": "es-MX-DaliaNeural",
        "Jorge - es-MX (Male)": "es-MX-JorgeNeural",
        "Federico - es-NI (Male)": "es-NI-FedericoNeural",
        "Yolanda - es-NI (Female)": "es-NI-YolandaNeural",
        "Margarita - es-PA (Female)": "es-PA-MargaritaNeural",
        "Roberto - es-PA (Male)": "es-PA-RobertoNeural",
        "Mario - es-PY (Male)": "es-PY-MarioNeural",
        "Tania - es-PY (Female)": "es-PY-TaniaNeural",
        "Alex - es-PE (Male)": "es-PE-AlexNeural",
        "Camila - es-PE (Female)": "es-PE-CamilaNeural",
        "Karina - es-PR (Female)": "es-PR-KarinaNeural",
        "Victor - es-PR (Male)": "es-PR-VictorNeural",
        "Alvaro - es-ES (Male)": "es-ES-AlvaroNeural",
        "Elvira - es-ES (Female)": "es-ES-ElviraNeural",
        "Alonso - es-US (Male)": "es-US-AlonsoNeural",
        "Paloma - es-US (Female)": "es-US-PalomaNeural",
        "Mateo - es-UY (Male)": "es-UY-MateoNeural",
        "Valentina - es-UY (Female)": "es-UY-ValentinaNeural",
        "Paola - es-VE (Female)": "es-VE-PaolaNeural",
        "Sebastian - es-VE (Male)": "es-VE-SebastianNeural",
        "Jajang - su-ID (Male)": "su-ID-JajangNeural",
        "Tuti - su-ID (Female)": "su-ID-TutiNeural",
        "Rafiki - sw-KE (Male)": "sw-KE-RafikiNeural",
        "Zuri - sw-KE (Female)": "sw-KE-ZuriNeural",
        "Daudi - sw-TZ (Male)": "sw-TZ-DaudiNeural",
        "Rehema - sw-TZ (Female)": "sw-TZ-RehemaNeural",
        "Mattias - sv-SE (Male)": "sv-SE-MattiasNeural",
        "Sofie - sv-SE (Female)": "sv-SE-SofieNeural",
        "Pallavi - ta-IN (Female)": "ta-IN-PallaviNeural",
        "Valluvar - ta-IN (Male)": "ta-IN-ValluvarNeural",
        "Kani - ta-MY (Female)": "ta-MY-KaniNeural",
        "Surya - ta-MY (Male)": "ta-MY-SuryaNeural",
        "Anbu - ta-SG (Male)": "ta-SG-AnbuNeural",
        "Venba - ta-SG (Female)": "ta-SG-VenbaNeural",
        "Kumar - ta-LK (Male)": "ta-LK-KumarNeural",
        "Saranya - ta-LK (Female)": "ta-LK-SaranyaNeural",
        "Mohan - te-IN (Male)": "te-IN-MohanNeural",
        "Shruti - te-IN (Female)": "te-IN-ShrutiNeural",
        "Niwat - th-TH (Male)": "th-TH-NiwatNeural",
        "Premwadee - th-TH (Female)": "th-TH-PremwadeeNeural",
        "Ahmet - tr-TR (Male)": "tr-TR-AhmetNeural",
        "Emel - tr-TR (Female)": "tr-TR-EmelNeural",
        "Ostap - uk-UA (Male)": "uk-UA-OstapNeural",
        "Polina - uk-UA (Female)": "uk-UA-PolinaNeural",
        "Gul - ur-IN (Female)": "ur-IN-GulNeural",
        "Salman - ur-IN (Male)": "ur-IN-SalmanNeural",
        "Asad - ur-PK (Male)": "ur-PK-AsadNeural",
        "Uzma - ur-PK (Female)": "ur-PK-UzmaNeural",
        "Madina - uz-UZ (Female)": "uz-UZ-MadinaNeural",
        "Sardor - uz-UZ (Male)": "uz-UZ-SardorNeural",
        "HoaiMy - vi-VN (Female)": "vi-VN-HoaiMyNeural",
        "NamMinh - vi-VN (Male)": "vi-VN-NamMinhNeural",
        "Aled - cy-GB (Male)": "cy-GB-AledNeural",
        "Nia - cy-GB (Female)": "cy-GB-NiaNeural",
        "Thando - zu-ZA (Female)": "zu-ZA-ThandoNeural",
        "Themba - zu-ZA (Male)": "zu-ZA-ThembaNeural"
    }
}


# Definir modelo de entrada para TTS
class TTSRequest(BaseModel):
    input: str
    voice: str



def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(string=True))

    return text
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
    audio_path = await text_to_speech(markdown_to_text(request.input), selected_voice)
    
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
    
