const { app, BrowserWindow, ipcMain } = require('electron');
const path  = require('path');
const { spawn } = require('child_process');

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
