# 🧠 Clasificador de Comentarios - Aplicación de Escritorio

Aplicación de escritorio desarrollada en **Electron** para analizar comentarios desde archivos Excel y clasificarlos automáticamente como **Fortalezas** u **Oportunidades**, usando procesamiento de lenguaje natural (NLP). Permite trabajar con SharePoint para sincronizar datos.

---

## 🚀 Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tuusuario/tu-repo.git
   cd tu-repo
   ```

2. Instala las dependencias:
   ```bash
   npm install
   ```

3. Inicia la aplicación:
   ```bash
   npm start
   ```

---

## 📁 Configuración del Entorno (.env)

Debes crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# SharePoint
SHAREPOINT_SITE_URL=
SHAREPOINT_USERNAME=
SHAREPOINT_PASSWORD=
SHAREPOINT_RELATIVE_URL=
SHAREPOINT_TARGET_FOLDER=

# Hugging Face
TOKEN=

# Columnas del Excel (no modificar si tu archivo ya tiene estos nombres)
COL_ID=ID
COL_FORT=Fortalezas
COL_OPOR=Oportunidades
COL_FORO=Nombre del foro observado
COL_FECHA=Hora de finalización
COL_GER=Gerencia a la que pertenece el/la observador/a
COL_DEP=Departamento donde se esta realizando CdR
COL_ROL=Rol del observador/a
```

---

## 🔑 ¿Cómo obtener los valores del `.env`?

### 🔹 1. Credenciales de SharePoint

Debes contar con acceso a un sitio SharePoint Online. Para obtener los datos:

| Variable | Explicación |
|---------|-------------|
| `SHAREPOINT_SITE_URL` | URL principal del sitio (ej: `https://tudominio.sharepoint.com/sites/nombre-del-sitio`) |
| `SHAREPOINT_USERNAME` | Tu correo institucional con acceso al SharePoint |
| `SHAREPOINT_PASSWORD` | Tu contraseña o [contraseña de aplicación](https://support.microsoft.com/es-es/account-billing/usar-contrase%C3%B1as-de-aplicaciones-con-aplicaciones-que-no-admiten-la-verificaci%C3%B3n-en-dos-pasos-0eeec0d2-cd72-4c96-87c1-6a12a4f7d811) si usas autenticación en dos pasos |
| `SHAREPOINT_RELATIVE_URL` | Parte del path después de `/sites/`, por ejemplo: `/sites/nombre-del-sitio` |
| `SHAREPOINT_TARGET_FOLDER` | Carpeta dentro del sitio donde se guardarán o buscarán los archivos Excel, por ejemplo: `Documentos/Feedback` |

> 📌 Si no tienes acceso, pide que te creen una cuenta o permisos en el sitio correspondiente.

---

### 🔹 2. Token de Hugging Face

1. Ve a [https://huggingface.co](https://huggingface.co) y crea una cuenta gratuita si no tienes una.
2. Una vez logueado, entra a [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
3. Haz clic en "New Token", ponle un nombre y selecciona el permiso "Read".
4. Copia el token generado y pégalo en el campo:

```env
TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Este token permite a la app usar modelos NLP alojados en Hugging Face para analizar textos.

---

## 🧾 Notas Adicionales

- El análisis de texto se realiza localmente usando Python y modelos de Hugging Face.
- El archivo `.csv` resultante con las clasificaciones se guarda automáticamente.
- Puedes editar los nombres de columnas en el `.env` si tu archivo Excel usa etiquetas distintas.

---

## 🛠️ Tecnologías Usadas

- Electron
- Node.js
- Python
- Hugging Face Transformers
- SharePlum (para conexión a SharePoint)
- dotenv

---

## 📄 Licencia

MIT License
