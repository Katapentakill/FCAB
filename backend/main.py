import os, sys, json
import pandas as pd
from io import BytesIO, StringIO
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import login
from dotenv import load_dotenv
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

# 🔐 Cargar variables del entorno
load_dotenv()

# SharePoint
site_url = os.getenv("SHAREPOINT_SITE_URL")
username = os.getenv("SHAREPOINT_USERNAME")
password = os.getenv("SHAREPOINT_PASSWORD")
relative_url = os.getenv("SHAREPOINT_RELATIVE_URL")  # archivo origen
target_folder_url = os.getenv("SHAREPOINT_TARGET_FOLDER")  # carpeta destino

# Columnas esperadas
COL_ID = os.getenv("COL_ID")
COL_FORT = os.getenv("COL_FORT")
COL_OPOR = os.getenv("COL_OPOR")
COL_FORO = os.getenv("COL_FORO")
COL_FECHA = os.getenv("COL_FECHA")
COL_GER = os.getenv("COL_GER")
COL_DEP = os.getenv("COL_DEP")
COL_ROL = os.getenv("COL_ROL")

# Validación de argumentos
if len(sys.argv) < 2:
    print("Uso: python main.py <token> [umbral]")
    sys.exit(1)

token = sys.argv[1]
UMBRAL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
login(token=token)

# 📥 Leer archivo CSV desde SharePoint
def leer_archivo_sharepoint():
    ctx_auth = AuthenticationContext(site_url)
    if not ctx_auth.acquire_token_for_user(username, password):
        raise Exception("Error de autenticación con SharePoint")

    ctx = ClientContext(site_url, ctx_auth)

    file = BytesIO()
    ctx.web.get_file_by_server_relative_url(relative_url).download(file).execute_query()
    file.seek(0)

    # Guardar para inspección si se desea
    with open("archivo_temporal.descargado", "wb") as debug:
        debug.write(file.getvalue())

    # Intentar como Excel
    try:
        df = pd.read_excel(file, engine='openpyxl')
        print("Archivo leído como Excel (.xlsx)")
    except Exception as e:
        print(f"Falló como Excel, intentando como CSV. Detalle: {e}")
        file.seek(0)
        df = pd.read_csv(file, encoding="utf-8")
        print("Archivo leído como CSV")

    return df
# 📤 Subir archivo CSV a SharePoint
def subir_excel_sharepoint(df: pd.DataFrame, nombre_archivo: str):
    ctx_auth = AuthenticationContext(site_url)
    if not ctx_auth.acquire_token_for_user(username, password):
        raise Exception("Autenticación con SharePoint fallida")

    ctx = ClientContext(site_url, ctx_auth)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    ctx.web.get_folder_by_server_relative_url(target_folder_url)\
        .upload_file(nombre_archivo, excel_buffer.read()).execute_query()
    print(f" '{nombre_archivo}' subido correctamente a SharePoint.")

# ▶️ Proceso principal
df = leer_archivo_sharepoint()

res, tipos, foros, fechas, ids, gers, deps, roles = ([] for _ in range(8))
for _, row in df.iterrows():
    for tipo, columna in [("Fortaleza", COL_FORT), ("Oportunidad", COL_OPOR)]:
        if pd.notna(row[columna]) and len(str(row[columna]).strip()) >= 6:
            res.append(str(row[columna]).strip())
            tipos.append(tipo)
            ids.append(row[COL_ID])
            foros.append(row[COL_FORO])
            gers.append(row[COL_GER])
            deps.append(row[COL_DEP])
            roles.append(row[COL_ROL])
            fechas.append(row[COL_FECHA])

# 🧠 Clasificación semántica
with open("backend/frases_clave.json", encoding="utf-8") as f:
    data = json.load(f)
temas = list(set(data["Fortalezas"] + data["Debilidades"]))

model = SentenceTransformer("distiluse-base-multilingual-cased-v1")
temas_emb = model.encode(temas, normalize_embeddings=True)

def asignar(txt):
    emb = model.encode(txt, normalize_embeddings=True)
    cos = util.cos_sim(emb, temas_emb)
    idx = cos.argmax().item(); score = cos[0, idx]
    return temas[idx] if score >= UMBRAL else "No clasificados"

cats = [asignar(t) for t in res]

# 💾 Guardar resultado
df_resultado = pd.DataFrame({
    "ID": ids, "respuesta": res, "foro": foros, "gerencia_observador": gers,
    "departamento": deps, "rol_observador": roles, "fecha": fechas,
    "tipo": tipos, "categoria_asignada": cats
})

nombre_excel = "Respuestas_Analisis.xlsx"
df_resultado.to_csv(nombre_excel, index=False, encoding="utf-8-sig")
print("Archivo generado con éxito")

# 🔼 Subida final
subir_excel_sharepoint(df_resultado, nombre_excel)
