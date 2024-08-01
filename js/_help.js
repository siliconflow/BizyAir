let app;
let ComfyWidgets;
let api;
let $el;

const loadModules = async () => {
  const pathname = window.location.pathname;
  const isRootPath = pathname === '/';
   
  const getPath = (relativePath) => `${isRootPath ? relativePath : pathname}scripts/`;

  
  const modulesPaths = {
    app: `${getPath('../../')}app.js`,
    widgets: `${getPath('../../../')}widgets.js`,
    api: `${getPath('../../../')}api.js`,
    $el: `${getPath('../../')}ui.js`
  };



  try {
    const [appModule, widgetsModule, apiModule, uiModule] = await Promise.all([
      import(modulesPaths.app),
      import(modulesPaths.widgets),
      import(modulesPaths.api),
      import(modulesPaths.$el)
    ]);

    app = appModule.app;
    ComfyWidgets = widgetsModule.ComfyWidgets;
    api = apiModule.api;
    $el = uiModule.$el;

  } catch (error) {
    console.error('Failed to load ComfyUI modules:', error);
    throw new Error('Module loading failed. Check console for details.');
  }
};

await loadModules();

export { app, ComfyWidgets, api, $el };