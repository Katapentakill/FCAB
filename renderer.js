/* ---------- Acceso al JSON ---------- */
const rutaJson = window.api.rutaJson;
console.log('🛠 Ruta JSON usada:', rutaJson);

/* ---------- Botón Ejecutar análisis ---------- */
document.getElementById('run').addEventListener('click', async () => {
  const estado = document.getElementById('estado');
  const ruta = window.api?.ONEDRIVE_URL;
  const token = window.api?.TOKEN;
  if (!ruta || !token) {
      estado.innerText = '❌ Faltan valores en .env (ruta o token).';
      return;
  }
  estado.innerText = ' Ejecutando…';

  try {
    const msg = await window.api.ejecutarPython({ ruta, token });
    estado.innerText = msg;
  } catch (err) {
    console.error(err);
    estado.innerText = '❌ Error al ejecutar.';
  }
});

/* ---------- CRUD de frases ---------- */
function cargarFrases () {
  const data = JSON.parse(window.fs.readFileSync(rutaJson, 'utf-8'));
  const listaFort = document.getElementById('lista-fortalezas');
  const listaDeb  = document.getElementById('lista-debilidades');
  listaFort.innerHTML = ''; listaDeb.innerHTML = '';

  data.Fortalezas.forEach((f,i)=>listaFort.appendChild(crearElemento(f,i,'Fortalezas')));
  data.Debilidades.forEach((f,i)=>listaDeb.appendChild(crearElemento(f,i,'Debilidades')));
}

function crearElemento (frase, idx, tipo) {
  const li = document.createElement('li');
  const span = document.createElement('span');
  span.textContent = frase; span.contentEditable = true;
  span.addEventListener('blur',()=>actualizarFrase(tipo,idx,span.textContent));
  span.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();span.blur();}});
  const btn = document.createElement('button');
  btn.textContent='❌'; btn.onclick=()=>eliminarFrase(tipo,idx);
  li.appendChild(span); li.appendChild(btn); return li;
}

function agregarFrase (tipo) {
  const inputId = tipo==='Fortalezas'?'nueva-fortaleza':'nueva-debilidad';
  const input = document.getElementById(inputId);
  const frase = input.value.trim(); if(!frase) return;
  const data = JSON.parse(window.fs.readFileSync(rutaJson,'utf-8'));
  if(data[tipo].includes(frase)){alert('⚠️ Frase ya existe.'); return;}
  data[tipo].push(frase);
  window.fs.writeFileSync(rutaJson,JSON.stringify(data,null,2),'utf-8');
  input.value=''; cargarFrases();
}

function eliminarFrase (tipo,idx){
  const data = JSON.parse(window.fs.readFileSync(rutaJson,'utf-8'));
  data[tipo].splice(idx,1);
  window.fs.writeFileSync(rutaJson,JSON.stringify(data,null,2),'utf-8');
  cargarFrases();
}

function actualizarFrase (tipo,idx,nuevo){
  const data = JSON.parse(window.fs.readFileSync(rutaJson,'utf-8'));
  const limpio = nuevo.trim();
  if(!limpio || data[tipo].includes(limpio)){cargarFrases(); return;}
  data[tipo][idx]=limpio;
  window.fs.writeFileSync(rutaJson,JSON.stringify(data,null,2),'utf-8');
}

window.addEventListener('DOMContentLoaded', cargarFrases);

/* ---------- Tema claro / oscuro ---------- */
const themeBtn=document.getElementById('toggleTheme');
if(themeBtn){
  const preferDark = localStorage.getItem('theme')==='dark';
  if(preferDark) document.body.classList.add('dark');
  themeBtn.addEventListener('click',()=>{
    document.body.classList.toggle('dark');
    const modo=document.body.classList.contains('dark')?'dark':'light';
    localStorage.setItem('theme',modo);
    themeBtn.textContent = modo==='dark'?'☀️':'🌙';
  });
}
