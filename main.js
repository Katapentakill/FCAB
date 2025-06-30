const { app, BrowserWindow, ipcMain } = require('electron');
const path  = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const dotenv = require('dotenv');
const rutaJsonAbsoluta = path.join(__dirname, 'backend', 'frases_clave.json');

function createWindow () {
  const win = new BrowserWindow({
    width : 1000,
    height: 800,
    icon: path.join(__dirname, 'assets', 'logo-fcab.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      additionalArguments: [`--jsonPath=${rutaJsonAbsoluta}`]
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

ipcMain.handle('ejecutar-python', async (_, args) => new Promise((res, rej) => {
  const rutaPython = path.join(__dirname, 'backend', 'main.py');
  console.log("Argumentos recibidos:", args)
  const proc = spawn('python', [rutaPython, args.token]);


  proc.stdout.on('data', d => console.log(d.toString()));
  proc.stderr.on('data', d => console.error(d.toString()));

  proc.on('close', code =>
    code === 0 ? res(' CSV generado correctamente')
               : rej (' Falló la ejecución del script')
  );
}));

ipcMain.handle('obtener-env', async () => {
  const envPath = path.join(__dirname, '.env');
  const envData = dotenv.parse(fs.readFileSync(envPath));
  return envData;
});

ipcMain.handle('guardar-env', async (_, datos) => {
  try {
    const envPath = path.join(__dirname, '.env');

    const todas = dotenv.parse(fs.readFileSync(envPath));
    const clavesCol = Object.keys(todas).filter(k => k.startsWith('COL_'));
    const colLines = clavesCol.map(k => `${k}=${todas[k]}`);

    const permitidas = [
      'SHAREPOINT_SITE_URL', 'SHAREPOINT_USERNAME', 'SHAREPOINT_PASSWORD',
      'SHAREPOINT_RELATIVE_URL', 'SHAREPOINT_TARGET_FOLDER'
    ];
    const nuevasLineas = permitidas.map(k => `${k}=${datos[k] ?? ''}`);

    const finalEnv = [...nuevasLineas, '', ...colLines].join('\n');
    fs.writeFileSync(envPath, finalEnv);
    return true;
  } catch (e) {
    console.error('❌ Error guardando .env:', e);
    return false;
  }
});

