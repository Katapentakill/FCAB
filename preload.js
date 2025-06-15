const { contextBridge, ipcRenderer } = require('electron');
const fs   = require('fs');
const path = require('path');

/* ruta del JSON pasada como argumento o fallback local */
const arg      = process.argv.find(a => a.startsWith('--jsonPath='));
const rutaJson = arg
  ? arg.replace('--jsonPath=', '')
  : path.join(__dirname, 'backend', 'frases_clave.json');

/* API segura para el renderer */
contextBridge.exposeInMainWorld('api', {
  ejecutarPython: (args) => ipcRenderer.invoke('ejecutar-python', args),
  rutaJson
});

contextBridge.exposeInMainWorld('fs', {
  readFileSync :(f,enc='utf-8') => fs.readFileSync(f,enc),
  writeFileSync:(f,d,enc='utf-8') => fs.writeFileSync(f,d,enc)
});

contextBridge.exposeInMainWorld('path', {
  join    : (...p) => path.join(...p),
  basename:  (p)   => path.basename(p)
});
