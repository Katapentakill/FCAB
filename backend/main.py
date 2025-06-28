import os, sys, json, requests, pandas as pd
from io import BytesIO
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()

# 💡 Enlace directo (OneDrive) permitido
ONEDRIVE_URL = os.getenv("ONEDRIVE_URL")
if not ONEDRIVE_URL:
    raise ValueError("Falta ONEDRIVE_URL en el archivo .env")

def resolver_onedrive(url: str) -> str:
    """Convierte un enlace de 1drv.ms en uno directo de descarga"""
    r = requests.head(url, allow_redirects=True)
    direct_url = r.url
    if "redir" not in direct_url:
        raise ValueError("No se pudo resolver el enlace de OneDrive.")
    # Cambiar el parámetro para forzar descarga
    return direct_url.replace("redir?", "download?")

def descargar_excel(url: str) -> BytesIO:
    if "1drv.ms" in url:
        url = resolver_onedrive(url)
    if "download=1" not in url:
        raise ValueError("El enlace debe terminar en un link de descarga directa")
    r = requests.get(url)
    r.raise_for_status()
    return BytesIO(r.content)

def leer_excel(src: str) -> pd.DataFrame:
    stream = descargar_excel(src) if src.startswith("http") else src
    if not src.startswith("http") and not os.path.exists(stream):
        raise FileNotFoundError("Excel no encontrado")
    return pd.ExcelFile(stream).parse("Sheet1")

# 🧾 Argumentos: ninguno requerido para ruta, ya que se fija el enlace
if len(sys.argv) < 2:
    print("Uso: python main.py <token> [umbral]")
    sys.exit(1)

token = os.getenv("TOKEN")
token = sys.argv[1]
UMBRAL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
login(token=token)

# 👉 Siempre se usa el enlace de OneDrive
df = leer_excel(ONEDRIVE_URL)

# 💬 Columnas esperadas
COL_ID = os.getenv("COL_ID")
COL_FORT = os.getenv("COL_FORT")
COL_OPOR = os.getenv("COL_OPOR")
COL_FORO = os.getenv("COL_FORO")
COL_FECHA = os.getenv("COL_FECHA")
COL_GER = os.getenv("COL_GER")
COL_DEP = os.getenv("COL_DEP")
COL_ROL = os.getenv("COL_ROL")

res, tipos, foros, fechas, ids, gers, deps, roles = ([] for _ in range(8))

for _, row in df.iterrows():
    if pd.notna(row[COL_FORT]) and len(str(row[COL_FORT]).strip()) >= 6:
        res.append(str(row[COL_FORT]).strip()); tipos.append("Fortaleza")
    if pd.notna(row[COL_OPOR]) and len(str(row[COL_OPOR]).strip()) >= 6:
        res.append(str(row[COL_OPOR]).strip()); tipos.append("Oportunidad")
    if tipos and len(tipos) == len(res):
        foros.append(row[COL_FORO]); fechas.append(row[COL_FECHA])
        ids.append(row[COL_ID]); gers.append(row[COL_GER])
        deps.append(row[COL_DEP]); roles.append(row[COL_ROL])

# 📚 Cargar frases clave
with open("backend/frases_clave.json", encoding="utf-8") as f:
    data = json.load(f)
temas = list(set(data["Fortalezas"] + data["Debilidades"]))

# 🔍 Modelo y clasificación
model = SentenceTransformer("distiluse-base-multilingual-cased-v1")
temas_emb = model.encode(temas, normalize_embeddings=True)

def asignar(txt):
    emb = model.encode(txt, normalize_embeddings=True)
    cos = util.cos_sim(emb, temas_emb)
    idx = cos.argmax().item(); score = cos[0, idx]
    return temas[idx] if score >= UMBRAL else "No clasificados"

cats = [asignar(t) for t in res]

# 💾 Guardar CSV de resultados
pd.DataFrame({
  "ID": ids, "respuesta": res, "foro": foros, "gerencia_observador": gers,
  "departamento": deps, "rol_observador": roles, "fecha": fechas,
  "tipo": tipos, "categoria_asignada": cats
}).to_csv("respuesta.csv", index=False, encoding="utf-8-sig")

print("✅ respuesta.csv generado con éxito")
