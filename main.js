const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      nodeIntegration: false
    }
  });

  // Load your hosted site
  win.loadURL("https://daily-planner-isea.onrender.com");
}

app.on('ready', createWindow);
