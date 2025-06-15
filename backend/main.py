import os, sys, json, requests, pandas as pd
from io import BytesIO
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import login

def descargar_excel(url:str)->BytesIO:
    if "download=1" not in url:
        raise ValueError("El enlace debe terminar en '&download=1'")
    r = requests.get(url); r.raise_for_status()
    return BytesIO(r.content)

def leer_excel(src:str)->pd.DataFrame:
    stream = descargar_excel(src) if src.startswith("http") else src
    if not src.startswith("http") and not os.path.exists(stream):
        raise FileNotFoundError("Excel no encontrado")
    return pd.ExcelFile(stream).parse("Sheet1")

if len(sys.argv) < 3:
    print("Uso: python main.py <ruta|link excel> <token> [umbral]")
    sys.exit(1)

path_excel, token = sys.argv[1], sys.argv[2]
UMBRAL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
login(token=token)

df = leer_excel(path_excel)

COL_ID="ID"; COL_FORT="Fortalezas"; COL_OPOR="Oportunidades"
COL_FORO="Nombre del foro observado"
COL_FECHA="Hora de finalización"
COL_GER="Gerencia a la que pertenece el/la observador/a"
COL_DEP="Departamento donde se esta realizando CdR"
COL_ROL="Rol del observador/a"

res, tipos, foros, fechas, ids, gers, deps, roles = ([] for _ in range(8))

for _,row in df.iterrows():
    if pd.notna(row[COL_FORT]) and len(str(row[COL_FORT]).strip())>=6:
        res.append(str(row[COL_FORT]).strip()); tipos.append("Fortaleza")
    if pd.notna(row[COL_OPOR]) and len(str(row[COL_OPOR]).strip())>=6:
        res.append(str(row[COL_OPOR]).strip()); tipos.append("Oportunidad")
    if tipos and len(tipos)==len(res):   # agregar campos paralelos
        foros.append(row[COL_FORO]); fechas.append(row[COL_FECHA])
        ids.append(row[COL_ID]); gers.append(row[COL_GER])
        deps.append(row[COL_DEP]); roles.append(row[COL_ROL])

with open("backend/frases_clave.json",encoding="utf-8") as f:
    data=json.load(f)
temas=list(set(data["Fortalezas"]+data["Debilidades"]))
model=SentenceTransformer("distiluse-base-multilingual-cased-v1")
temas_emb=model.encode(temas,normalize_embeddings=True)

def asignar(txt):
    emb=model.encode(txt,normalize_embeddings=True)
    cos=util.cos_sim(emb,temas_emb); idx=cos.argmax().item(); score=cos[0,idx]
    return temas[idx] if score>=UMBRAL else "No clasificados"

cats=[asignar(t) for t in res]

pd.DataFrame({
  "ID":ids,"respuesta":res,"foro":foros,"gerencia_observador":gers,
  "departamento":deps,"rol_observador":roles,"fecha":fechas,
  "tipo":tipos,"categoria_asignada":cats
}).to_csv("respuesta.csv",index=False,encoding="utf-8-sig")

print(" respuesta.csv generado con éxito")
