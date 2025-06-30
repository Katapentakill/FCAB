const { contextBridge, ipcRenderer } = require('electron');
const fs   = require('fs');
const path = require('path');
require('dotenv').config();
/* ruta del JSON pasada como argumento o fallback local */
const arg      = process.argv.find(a => a.startsWith('--jsonPath='));
const rutaJson = arg
  ? arg.replace('--jsonPath=', '')
  : path.join(__dirname, 'backend', 'frases_clave.json');

/* API segura para el renderer */
contextBridge.exposeInMainWorld('api', {
  ejecutarPython: (args) => ipcRenderer.invoke('ejecutar-python', args),
  rutaJson,
  TOKEN: process.env.TOKEN,
  COL_ID: process.env.COL_ID,
  COL_FORT: process.env.COL_FORT,
  COL_OPOR: process.env.COL_OPOR,
  COL_FORO: process.env.COL_FORO,
  COL_FECHA: process.env.COL_FECHA,
  COL_GER: process.env.COL_GER,
  COL_DEP: process.env.COL_DEP,
  COL_ROL: process.env.COL_ROL,
});

contextBridge.exposeInMainWorld('fs', {
  readFileSync :(f,enc='utf-8') => fs.readFileSync(f,enc),
  writeFileSync:(f,d,enc='utf-8') => fs.writeFileSync(f,d,enc)
});

contextBridge.exposeInMainWorld('path', {
  join    : (...p) => path.join(...p),
  basename:  (p)   => path.basename(p)
});
