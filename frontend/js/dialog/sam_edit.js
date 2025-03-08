import { api } from "../../../scripts/api.js";
import { ComfyApp } from "../../../scripts/app.js";
import { $el, ComfyDialog, } from "../../../scripts/ui.js";

function loadImage(imagePath) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = function() {
        resolve(image);
      };
      image.src = imagePath;
    });
  }
function prepare_mask(image, maskCanvas, maskCtx, maskColor) {
    maskCtx.drawImage(image, 0, 0, maskCanvas.width, maskCanvas.height);
    const maskData = maskCtx.getImageData(
      0,
      0,
      maskCanvas.width,
      maskCanvas.height
    );
    for (let i = 0; i < maskData.data.length; i += 4) {
      if (maskData.data[i + 3] == 255) maskData.data[i + 3] = 0;
      else if(maskData.data[i + 3] == 0){   //对应黑色点
        maskData.data[i + 3] = 255;
        maskData.data[i] = 0;
        maskData.data[i + 1] = 0;
        maskData.data[i + 2] = 0;
      }
      else{               //对应红色点254
        maskData.data[i + 3] = 255;
        maskData.data[i] = 255;
        maskData.data[i + 1] = 0;
        maskData.data[i + 2] = 0;
      }
    }
    maskCtx.globalCompositeOperation = "source-over";
    maskCtx.putImageData(maskData, 0, 0);
}

function dataURLToBlob(dataURL) {
  const parts = dataURL.split(";base64,");
  const contentType = parts[0].split(":")[1];
  const byteString = atob(parts[1]);
  const arrayBuffer = new ArrayBuffer(byteString.length);
  const uint8Array = new Uint8Array(arrayBuffer);
  for (let i = 0; i < byteString.length; i++) {
    uint8Array[i] = byteString.charCodeAt(i);
  }
  return new Blob([arrayBuffer], { type: contentType });
}
async function uploadMask(filepath, formData) {
  await api.fetchApi("/upload/mask", {
    method: "POST",
    body: formData
  }).then((response) => {
  }).catch((error) => {
    console.error("Error:", error);
  });
  ComfyApp.clipspace.imgs[ComfyApp.clipspace["selectedIndex"]] = new Image();
  ComfyApp.clipspace.imgs[ComfyApp.clipspace["selectedIndex"]].src = api.apiURL(
    "/view?" + new URLSearchParams(filepath).toString() + app.getPreviewFormatParam() + app.getRandParam()
  );
  if (ComfyApp.clipspace.images)
    ComfyApp.clipspace.images[ComfyApp.clipspace["selectedIndex"]] = filepath;
  if (ComfyApp.clipspace && ComfyApp.clipspace.imgs && ComfyApp.clipspace.imgs.length > 0) {
    const img_preview = document.getElementById(
      "clipspace_preview"
    );
    if (img_preview) {
      img_preview.src = ComfyApp.clipspace.imgs[ComfyApp.clipspace["selectedIndex"]].src;
      img_preview.style.maxHeight = "100%";
      img_preview.style.maxWidth = "100%";
    }
  }
}
async function uploadSamPrompt(formData){
  await api.fetchApi("/bizyair/postsam", {
    method: "POST",
    body: formData
  }).then((response) => {
  }).catch((error) => {
    console.error("Error:", error);
  });
}

class SAMEditorDialog extends ComfyDialog {
    static instance = null;
    static mousedown_x = null;
    static mousedown_y = null;
    static dragging = false;
    static mousedown = null;
    brush;
    maskCtx;
    maskCanvas;
    brush_size_slider;
    brush_opacity_slider;
    pointButton;
    saveButton;
    zoom_ratio;
    pan_x;
    pan_y;
    imgCanvas;
    last_display_style;
    is_visible;
    image;
    handler_registered;
    brush_slider_input;
    cursorX;
    cursorY;
    mousedown_pan_x;
    mousedown_pan_y;
    last_pressure;
    history = [];
    coords = [];
    filename = " ";
    static getInstance() {
      if (!SAMEditorDialog.instance) {
        SAMEditorDialog.instance = new SAMEditorDialog();
      }
      return SAMEditorDialog.instance;
    }

    is_layout_created = false;
    constructor() {
      super();
      this.element = $el("div.comfy-modal", { parent: document.body }, [
        $el("div.comfy-modal-content", [...this.createButtons()])
      ]);
    }
    createButtons() {
      return [];
    }
    createButton(name, callback) {
      var button = document.createElement("button");
      button.style.pointerEvents = "auto";
      button.innerText = name;
      button.addEventListener("click", callback);
      return button;
    }
    createLeftButton(name, callback) {
      var button = this.createButton(name, callback);
      button.style.cssFloat = "left";
      button.style.marginRight = "4px";
      return button;
    }
    createRightButton(name, callback) {
      var button = this.createButton(name, callback);
      button.style.cssFloat = "right";
      button.style.marginLeft = "4px";
      return button;
    }
    createLeftSlider(self, name, callback) {
      const divElement = document.createElement("div");
      divElement.id = "maskeditor-slider";
      divElement.style.cssFloat = "left";
      divElement.style.fontFamily = "sans-serif";
      divElement.style.marginRight = "4px";
      divElement.style.color = "var(--input-text)";
      divElement.style.backgroundColor = "var(--comfy-input-bg)";
      divElement.style.borderRadius = "8px";
      divElement.style.borderColor = "var(--border-color)";
      divElement.style.borderStyle = "solid";
      divElement.style.fontSize = "15px";
      divElement.style.height = "21px";
      divElement.style.padding = "1px 6px";
      divElement.style.display = "flex";
      divElement.style.position = "relative";
      divElement.style.top = "2px";
      divElement.style.pointerEvents = "auto";
      self.brush_slider_input = document.createElement("input");
      self.brush_slider_input.setAttribute("type", "range");
      self.brush_slider_input.setAttribute("min", "1");
      self.brush_slider_input.setAttribute("max", "100");
      self.brush_slider_input.setAttribute("value", "10");
      const labelElement = document.createElement("label");
      labelElement.textContent = name;
      divElement.appendChild(labelElement);
      divElement.appendChild(self.brush_slider_input);
      self.brush_slider_input.addEventListener("change", callback);
      return divElement;
    }
    createOpacitySlider(self, name, callback) {
      const divElement = document.createElement("div");
      divElement.id = "maskeditor-opacity-slider";
      divElement.style.cssFloat = "left";
      divElement.style.fontFamily = "sans-serif";
      divElement.style.marginRight = "4px";
      divElement.style.color = "var(--input-text)";
      divElement.style.backgroundColor = "var(--comfy-input-bg)";
      divElement.style.borderRadius = "8px";
      divElement.style.borderColor = "var(--border-color)";
      divElement.style.borderStyle = "solid";
      divElement.style.fontSize = "15px";
      divElement.style.height = "21px";
      divElement.style.padding = "1px 6px";
      divElement.style.display = "flex";
      divElement.style.position = "relative";
      divElement.style.top = "2px";
      divElement.style.pointerEvents = "auto";
      self.opacity_slider_input = document.createElement("input");
      self.opacity_slider_input.setAttribute("type", "range");
      self.opacity_slider_input.setAttribute("min", "0.1");
      self.opacity_slider_input.setAttribute("max", "1.0");
      self.opacity_slider_input.setAttribute("step", "0.01");
      self.opacity_slider_input.setAttribute("value", "0.7");
      const labelElement = document.createElement("label");
      labelElement.textContent = name;
      divElement.appendChild(labelElement);
      divElement.appendChild(self.opacity_slider_input);
      self.opacity_slider_input.addEventListener("input", callback);
      return divElement;
    }
    setlayout(imgCanvas, maskCanvas) {
      const self = this;
      var bottom_panel = document.createElement("div");
      bottom_panel.style.position = "absolute";
      bottom_panel.style.bottom = "0px";
      bottom_panel.style.left = "20px";
      bottom_panel.style.right = "20px";
      bottom_panel.style.height = "50px";
      bottom_panel.style.pointerEvents = "none";
      var brush = document.createElement("div");
      brush.id = "brush";
      brush.style.backgroundColor = "transparent";
      brush.style.outline = "1px dashed black";
      brush.style.boxShadow = "0 0 0 1px white";
      brush.style.borderRadius = "50%";
      brush.style.MozBorderRadius = "50%";
      brush.style.WebkitBorderRadius = "50%";
      brush.style.position = "absolute";
      brush.style.zIndex = "8889";
      brush.style.pointerEvents = "none";
      this.brush = brush;
      this.element.appendChild(imgCanvas);
      this.element.appendChild(maskCanvas);
      this.element.appendChild(bottom_panel);
      document.body.appendChild(brush);
      var clearButton = this.createLeftButton("Clear", () => {
        this.resetHistory();
        self.maskCtx.clearRect(
          0,
          0,
          self.maskCanvas.width,
          self.maskCanvas.height
        );
        this.addHistory();
      });
      var undoButton = this.createLeftButton("Undo", () => {
        this.undo();
        this.showLastHistory();
      });
      this.brush_size_slider = this.createLeftSlider(
        self,
        "Thickness",
        (event) => {
          self.brush_size = event.target.value;
          self.updateBrushPreview(self);
        }
      );
      this.brush_opacity_slider = this.createOpacitySlider(
        self,
        "Opacity",
        (event) => {
          self.brush_opacity = event.target.value;
          self.maskCanvas.style.opacity = self.brush_opacity.toString();
        }
      );
      this.pointButton = this.createLeftButton(this.getPointButtonText(), () => {
        if (self.brush_color_mode === "remain") {
          self.brush_color_mode = "remove";
        } else if (self.brush_color_mode === "remove") {
          self.brush_color_mode = "remain";
        } else {

        }
        self.updateWhenBrushColorModeChanged();
      });
      this.modeButton = this.createLeftButton(this.getModeButtonText(), () => {
        if (self.mode === "point") {
          self.mode = "box";
        } else if (self.mode === "box") {
          self.mode = "point";
        } else {

        }
        this.modeButton.innerText = this.getModeButtonText();
        this.resetHistory();
        self.maskCtx.clearRect(
          0,
          0,
          self.maskCanvas.width,
          self.maskCanvas.height
        );
        this.addHistory();
      });
      var cancelButton = this.createRightButton("Cancel", () => {
        document.removeEventListener("keydown", SAMEditorDialog.handleKeyDown);
        self.close();
      });
      this.saveButton = this.createRightButton("Save", () => {
        document.removeEventListener("keydown", SAMEditorDialog.handleKeyDown);
        self.save();
      });
      this.element.appendChild(imgCanvas);
      this.element.appendChild(maskCanvas);
      this.element.appendChild(bottom_panel);
      bottom_panel.appendChild(clearButton);
      bottom_panel.appendChild(undoButton);
      bottom_panel.appendChild(this.saveButton);
      bottom_panel.appendChild(cancelButton);
      bottom_panel.appendChild(this.brush_size_slider);
      bottom_panel.appendChild(this.brush_opacity_slider);
      bottom_panel.appendChild(this.pointButton);
      bottom_panel.appendChild(this.modeButton);
      imgCanvas.style.position = "absolute";
      maskCanvas.style.position = "absolute";
      imgCanvas.style.top = "200";
      imgCanvas.style.left = "0";
      maskCanvas.style.top = imgCanvas.style.top;
      maskCanvas.style.left = imgCanvas.style.left;
      const maskCanvasStyle = this.getMaskCanvasStyle();
      maskCanvas.style.mixBlendMode = maskCanvasStyle.mixBlendMode;
      maskCanvas.style.opacity = maskCanvasStyle.opacity.toString();
    }
    async show() {
      this.zoom_ratio = 1;
      this.pan_x = 0;
      this.pan_y = 0;
      if (!this.is_layout_created) {
        const imgCanvas = document.createElement("canvas");
        const maskCanvas = document.createElement("canvas");
        imgCanvas.id = "imageCanvas";
        maskCanvas.id = "maskCanvas";
        this.setlayout(imgCanvas, maskCanvas);
        this.imgCanvas = imgCanvas;
        this.maskCanvas = maskCanvas;
        this.maskCtx = maskCanvas.getContext("2d", { willReadFrequently: true });
        this.setEventHandler(maskCanvas);
        this.is_layout_created = true;
        const self = this;

        const observer = new MutationObserver(function(mutations) {
          mutations.forEach(function(mutation) {
            if (mutation.type === "attributes" && mutation.attributeName === "style") {
              if (self.last_display_style && self.last_display_style != "none" && self.element.style.display == "none") {
                self.brush.style.display = "none";
                ComfyApp.onClipspaceEditorClosed();
              }
              self.last_display_style = self.element.style.display;
            }
          });
        });
        const config = { attributes: true };
        observer.observe(this.element, config);
      }
      document.addEventListener("keydown", SAMEditorDialog.handleKeyDown);
      if (ComfyApp.clipspace_return_node) {
        this.saveButton.innerText = "Save to node";
      } else {
        this.saveButton.innerText = "Save";
      }
      this.saveButton.disabled = false;
      this.element.style.display = "block";
      this.element.style.width = "85%";
      this.element.style.margin = "0 7.5%";
      this.element.style.height = "100vh";
      this.element.style.top = "50%";
      this.element.style.left = "42%";
      this.element.style.zIndex = "8888";
      await this.setImages(this.imgCanvas);
      this.is_visible = true;
      const resp = await api.fetchApi("/bizyair/isresetsam");
      const status = await resp.json();

      if(status['isresetsam']){
        this.resetHistory();
      }

      const resp1 = await api.fetchApi("/bizyair/getsam");

      const sam_old_coords = await resp1.json();

      if(sam_old_coords.filename === this.filename){
        let sam_coords;
        if(sam_old_coords.mode == 1){
          sam_coords = sam_old_coords.point_coords;
        }
        else{
          sam_coords = sam_old_coords.box_coords;
        }
        for (const key in sam_coords) {
          if (sam_old_coords.hasOwnProperty(key)) {
            const value = sam_old_coords[key]
            this.coords.push(value);
          }
        }
      }
      else{
        this.resetHistory();
      }

      this.addHistory();
    }
    isOpened() {
      return this.element.style.display == "block";
    }
    invalidateCanvas(orig_image, mask_image) {
      this.imgCanvas.width = orig_image.width;
      this.imgCanvas.height = orig_image.height;
      this.maskCanvas.width = orig_image.width;
      this.maskCanvas.height = orig_image.height;
      let imgCtx = this.imgCanvas.getContext("2d", { willReadFrequently: true });
      let maskCtx = this.maskCanvas.getContext("2d", {
        willReadFrequently: true
      });
      imgCtx.drawImage(orig_image, 0, 0, orig_image.width, orig_image.height);
      prepare_mask(mask_image, this.maskCanvas, maskCtx, this.getMaskColor());
    }
    async setImages(imgCanvas) {
      let self = this;
      const imgCtx = imgCanvas.getContext("2d", { willReadFrequently: true });
      const maskCtx = this.maskCtx;
      const maskCanvas = this.maskCanvas;
      imgCtx.clearRect(0, 0, this.imgCanvas.width, this.imgCanvas.height);
      maskCtx.clearRect(0, 0, this.maskCanvas.width, this.maskCanvas.height);
      const filepath = ComfyApp.clipspace.images;
      const alpha_url = new URL(
        ComfyApp.clipspace.imgs[ComfyApp.clipspace["selectedIndex"]].src
      );
      alpha_url.searchParams.delete("channel");
      alpha_url.searchParams.delete("preview");
      alpha_url.searchParams.set("channel", "a");
      let mask_image = await loadImage(alpha_url);
      const rgb_url = new URL(
        ComfyApp.clipspace.imgs[ComfyApp.clipspace["selectedIndex"]].src
      );
      const href = rgb_url.href
      const filenameRegex = /filename=(.+?)(&|$)/;
      const match = href.match(filenameRegex);
      if (match) {
          this.filename = match[1].split('%20%5Binput%5D')[0];
          console.log("提取到的filename:", this.filename);
      } else {
          console.log("未找到filename匹配");
      }

      rgb_url.searchParams.delete("channel");
      rgb_url.searchParams.set("channel", "rgb");
      this.image = new Image();
      this.image.onload = function() {
        maskCanvas.width = self.image.width;
        maskCanvas.height = self.image.height;
        self.invalidateCanvas(self.image, mask_image);
        self.initializeCanvasPanZoom();
      };
      this.image.src = rgb_url.toString();
    }
    initializeCanvasPanZoom() {
      let drawWidth = this.image.width;
      let drawHeight = this.image.height;
      let width = this.element.clientWidth;
      let height = this.element.clientHeight;
      if (this.image.width > width) {
        drawWidth = width;
        drawHeight = drawWidth / this.image.width * this.image.height;
      }
      if (drawHeight > height) {
        drawHeight = height;
        drawWidth = drawHeight / this.image.height * this.image.width;
      }
      this.zoom_ratio = drawWidth / this.image.width;
      const canvasX = (width - drawWidth) / 2;
      const canvasY = (height - drawHeight) / 2;
      this.pan_x = canvasX;
      this.pan_y = canvasY;
      this.invalidatePanZoom();
    }
    invalidatePanZoom() {
      let raw_width = this.image.width * this.zoom_ratio;
      let raw_height = this.image.height * this.zoom_ratio;
      if (this.pan_x + raw_width < 10) {
        this.pan_x = 10 - raw_width;
      }
      if (this.pan_y + raw_height < 10) {
        this.pan_y = 10 - raw_height;
      }
      let width = `${raw_width}px`;
      let height = `${raw_height}px`;
      let left = `${this.pan_x}px`;
      let top = `${this.pan_y}px`;
      this.maskCanvas.style.width = width;
      this.maskCanvas.style.height = height;
      this.maskCanvas.style.left = left;
      this.maskCanvas.style.top = top;
      this.imgCanvas.style.width = width;
      this.imgCanvas.style.height = height;
      this.imgCanvas.style.left = left;
      this.imgCanvas.style.top = top;
    }
    setEventHandler(maskCanvas) {
      const self = this;
      if (!this.handler_registered) {
          this.element.addEventListener(
            "wheel",
            (event) => this.handleWheelEvent(self, event)
          );

          this.element.addEventListener("dragstart", (event) => {
            if (event.ctrlKey) {
              event.preventDefault();
            }
          });
          maskCanvas.addEventListener(
            "pointerdown",
            (event) => this.handlePointerDown(self, event)
          );
          maskCanvas.addEventListener(
            "pointermove",
            (event) => this.draw_move(self, event)
          );

          maskCanvas.addEventListener("pointerover", (event) => {
            this.brush.style.display = "block";
          });
          maskCanvas.addEventListener("pointerleave", (event) => {
            this.brush.style.display = "none";
          });

        maskCanvas.addEventListener(
            "pointerup",
            (event) => this.handlePointerUp(self, event)
          );
          this.handler_registered = true;
      }
    }
    getMaskCanvasStyle() {
      if (this.brush_color_mode === "negative") {
        return {
          mixBlendMode: "difference",
          opacity: "1"
        };
      } else {
        return {
          mixBlendMode: "initial",
          opacity: this.brush_opacity
        };
      }
    }
    getMaskColor() {
      if (this.brush_color_mode === "remain") {
        return { r: 0, g: 0, b: 0 };  //black
      }
      if (this.brush_color_mode === "remove") {
        return { r: 255, g: 0, b: 0 };  //red
      }
      return { r: 0, g: 0, b: 0 };
    }
    getMaskFillStyle() {
      const maskColor = this.getMaskColor();
      return "rgb(" + maskColor.r + "," + maskColor.g + "," + maskColor.b + ")";
    }
    getPointButtonText() {
      let colorCaption = "unknown";
      if (this.brush_color_mode === "remain") {
        colorCaption = "remain";
      } else if (this.brush_color_mode === "remove") {
        colorCaption = "remove";
      }
      return "Point mode: " + colorCaption;
    }
    getModeButtonText() {
      let modeCaption = "unknown";
      if (this.mode === "point") {
        modeCaption = "point";
      } else if (this.mode === "box") {
        modeCaption = "box";
      }
      return "Select mode: " + modeCaption;
    }
    updateWhenBrushColorModeChanged() {
      this.pointButton.innerText = this.getPointButtonText();
      const maskCanvasStyle = this.getMaskCanvasStyle();
      this.maskCanvas.style.mixBlendMode = maskCanvasStyle.mixBlendMode;
      this.maskCanvas.style.opacity = maskCanvasStyle.opacity.toString();
    }

    brush_opacity = 0.7;
    brush_size = 10;
    brush_color_mode = "remain";
    drawing_mode = false;
    lastx = -1;
    lasty = -1;
    lasttime = 0;
    endx = 0;
    endy = 0;
    startx = 0;
    starty = 0;
    mode = "point";
    static handleKeyDown(event) {
      const self = SAMEditorDialog.instance;
      if (event.key === "]") {
        self.brush_size = Math.min(self.brush_size + 2, 100);
        self.brush_slider_input.value = self.brush_size;
      } else if (event.key === "[") {
        self.brush_size = Math.max(self.brush_size - 2, 1);
        self.brush_slider_input.value = self.brush_size;
      } else if (event.key === "Enter") {
        self.save();
      }
      self.updateBrushPreview(self);
    }
    handlePointerUp(self, event) {
        event.preventDefault();

        if(self.mode === "box"){
          self.maskCtx.beginPath();
          if (!event.altKey && event.button == 0) {
              self.maskCtx.fillStyle = this.getMaskFillStyle();
              self.maskCtx.globalCompositeOperation = "source-over";
          } else {
              self.maskCtx.globalCompositeOperation = "destination-out";
          }
          var left = self.startx;
          var top = self.starty
          var w = self.endx - self.startx
          var h = self.endy - self.starty
          self.maskCtx.rect(left, top, w, h);
          self.maskCtx.fill();
        }
        if(self.mode === "box" && this.startx == this.endx && this.starty === this.endy){

        }
        else{
          this.addHistory();
          this.add_coords();
        }

        this.mousedown_x = null;
        this.mousedown_y = null;
        SAMEditorDialog.instance.drawing_mode = false;
    }
    updateBrushPreview(self) {
      const brush = self.brush;
      var centerX = self.cursorX;
      var centerY = self.cursorY;
      brush.style.width = self.brush_size * 2 * this.zoom_ratio + "px";
      brush.style.height = self.brush_size * 2 * this.zoom_ratio + "px";
      brush.style.left = centerX - self.brush_size * this.zoom_ratio + "px";
      brush.style.top = centerY - self.brush_size * this.zoom_ratio + "px";
    }
    handleWheelEvent(self, event) {
      event.preventDefault();
      if (event.ctrlKey) {
        if (event.deltaY < 0) {
          this.zoom_ratio = Math.min(10, this.zoom_ratio + 0.2);
        } else {
          this.zoom_ratio = Math.max(0.2, this.zoom_ratio - 0.2);
        }
        this.invalidatePanZoom();
      } else {
        if (event.deltaY < 0) this.brush_size = Math.min(this.brush_size + 2, 100);
        else this.brush_size = Math.max(this.brush_size - 2, 1);
        this.brush_slider_input.value = this.brush_size.toString();
        this.updateBrushPreview(this);
      }
    }
    pointMoveEvent(self, event) {
      this.cursorX = event.pageX;
      this.cursorY = event.pageY;
      self.updateBrushPreview(self);
      if (event.ctrlKey) {
        event.preventDefault();
        self.pan_move(self, event);
      }
      let left_button_down = window.TouchEvent && event instanceof TouchEvent || event.buttons == 1;
      if (event.shiftKey && left_button_down) {
        self.drawing_mode = false;
        const y = event.clientY;
        let delta = (self.zoom_lasty - y) * 5e-3;
        self.zoom_ratio = Math.max(
          Math.min(10, self.last_zoom_ratio - delta),
          0.2
        );
        this.invalidatePanZoom();
        return;
      }
    }
    pan_move(self, event) {
      if (event.buttons == 1) {
        if (SAMEditorDialog.mousedown_x) {
          let deltaX = SAMEditorDialog.mousedown_x - event.clientX;
          let deltaY = SAMEditorDialog.mousedown_y - event.clientY;
          self.pan_x = this.mousedown_pan_x - deltaX;
          self.pan_y = this.mousedown_pan_y - deltaY;
          self.invalidatePanZoom();
        }
      }
    }

    draw_move(self, event) {
      if (event.ctrlKey || event.shiftKey) {
        return;
      }
      event.preventDefault();
      this.cursorX = event.pageX;
      this.cursorY = event.pageY;
      self.updateBrushPreview(self);
      let left_button_down = window.TouchEvent && event instanceof TouchEvent || event.buttons == 1;
      let right_button_down = [2, 5, 32].includes(event.buttons);
      if (!event.altKey && left_button_down) {
        var diff = performance.now() - self.lasttime;
        const maskRect = self.maskCanvas.getBoundingClientRect();
        var x = event.offsetX;
        var y = event.offsetY;
        if (event.offsetX == null) {
          x = event.targetTouches[0].clientX - maskRect.left;
        }
        if (event.offsetY == null) {
          y = event.targetTouches[0].clientY - maskRect.top;
        }
        x /= self.zoom_ratio;
        y /= self.zoom_ratio;
        var brush_size = 3;
        if (event instanceof PointerEvent && event.pointerType == "pen") {
          brush_size *= event.pressure;
          this.last_pressure = event.pressure;
        } else if (window.TouchEvent && event instanceof TouchEvent && diff < 20) {
          brush_size *= this.last_pressure;
        } else {
          brush_size = 3;
        }
        if (diff > 20 && !this.drawing_mode)
          requestAnimationFrame(() => {
            self.maskCtx.beginPath();
            self.maskCtx.fillStyle = this.getMaskFillStyle();
            self.maskCtx.globalCompositeOperation = "source-over";
            self.maskCtx.arc(x, y, brush_size, 0, Math.PI * 2, false);
            self.maskCtx.rect(x, y, 20, 30);
            self.maskCtx.fill();
            self.lastx = x;
            self.lasty = y;
          });
        else
          requestAnimationFrame(() => {
            this.showLastHistory() // 每次绘制先清除上一次
            self.maskCtx.save();
            self.maskCtx.beginPath();
            self.maskCtx.fillStyle = this.getMaskFillStyle();
            self.maskCtx.globalCompositeOperation = "source-over";
            var dx = x - self.lastx;
            var dy = y - self.lasty;
            var distance = Math.sqrt(dx * dx + dy * dy);
            var directionX = dx / distance;
            var directionY = dy / distance;
            for (var i = 0; i < distance; i += 5) {
              var px = self.lastx + directionX * i;
              var py = self.lasty + directionY * i;
              if(self.mode === "box"){
                self.endx = px;
                self.endy = py;
                var left = self.endx > self.startx ? self.startx : self.endx
                var top = self.endy > self.starty ? self.starty : self.endy
                var w = Math.abs(self.endx - self.startx)
                var h = Math.abs(self.endy -  self.starty)

                self.maskCtx.rect(left, top, w, h);

                self.maskCtx.stroke();
                self.maskCtx.restore();
              }

            }
            self.lastx = x;
            self.lasty = y;
          });
        self.lasttime = performance.now();
      } else if (event.altKey && left_button_down || right_button_down) {
        const maskRect = self.maskCanvas.getBoundingClientRect();
        const x2 = (event.offsetX || event.targetTouches[0].clientX - maskRect.left) / self.zoom_ratio;
        const y2 = (event.offsetY || event.targetTouches[0].clientY - maskRect.top) / self.zoom_ratio;
        var brush_size = this.brush_size;
        if (event instanceof PointerEvent && event.pointerType == "pen") {
          brush_size *= event.pressure;
          this.last_pressure = event.pressure;
        } else if (window.TouchEvent && event instanceof TouchEvent && diff < 20) {
          brush_size *= this.last_pressure;
        } else {
          brush_size = this.brush_size;
        }
        if (diff > 20 && !this.drawing_mode)
          requestAnimationFrame(() => {
            self.maskCtx.beginPath();
            self.maskCtx.globalCompositeOperation = "destination-out";
            self.maskCtx.arc(x2, y2, brush_size, 0, Math.PI * 2, false);
            self.maskCtx.fill();
            self.lastx = x2;
            self.lasty = y2;
          });
        else
          requestAnimationFrame(() => {
            self.maskCtx.beginPath();
            self.maskCtx.globalCompositeOperation = "destination-out";
            var dx = x2 - self.lastx;
            var dy = y2 - self.lasty;
            var distance = Math.sqrt(dx * dx + dy * dy);
            var directionX = dx / distance;
            var directionY = dy / distance;
            for (var i = 0; i < distance; i += 5) {
              var px = self.lastx + directionX * i;
              var py = self.lasty + directionY * i;
              self.maskCtx.arc(px, py, brush_size, 0, Math.PI * 2, false);
              self.maskCtx.fill();
            }
            self.lastx = x2;
            self.lasty = y2;
          });
        self.lasttime = performance.now();
      }
    }
    handlePointerDown(self, event) {
        if (event.ctrlKey) {
          if (event.buttons == 1) {
            SAMEditorDialog.mousedown_x = event.clientX;
            SAMEditorDialog.mousedown_y = event.clientY;
            this.mousedown_pan_x = this.pan_x;
            this.mousedown_pan_y = this.pan_y;
          }
          return;
        }
        var brush_size = this.brush_size;
        if (event instanceof PointerEvent && event.pointerType == "pen") {
          brush_size *= event.pressure;
          this.last_pressure = event.pressure;
        }
        if ([0, 2, 5].includes(event.button)) {
          self.drawing_mode = true;
          event.preventDefault();
          if (event.shiftKey) {
            self.zoom_lasty = event.clientY;
            self.last_zoom_ratio = self.zoom_ratio;
            return;
          }
          const maskRect = self.maskCanvas.getBoundingClientRect();
          const x = (event.offsetX || event.targetTouches[0].clientX - maskRect.left) / self.zoom_ratio;
          const y = (event.offsetY || event.targetTouches[0].clientY - maskRect.top) / self.zoom_ratio;

          if (!event.altKey && event.button == 0) {
            self.maskCtx.fillStyle = this.getMaskFillStyle();
            self.maskCtx.globalCompositeOperation = "source-over";
          } else {
            self.maskCtx.globalCompositeOperation = "destination-out";
          }
          if(self.mode === "point"){
              self.maskCtx.beginPath();
              self.maskCtx.arc(x, y, brush_size, 0, Math.PI * 2, false);
              self.maskCtx.fill();
              self.startx = x;
              self.starty = y;
          }
          else if(self.mode === "box"){
            self.startx = x;
            self.starty = y;
          }

          self.lastx = x;
          self.lasty = y;
          self.lasttime = performance.now();
        }

    }
    async save() {
      const backupCanvas = document.createElement("canvas");
      const backupCtx = backupCanvas.getContext("2d", {
        willReadFrequently: true
      });
      backupCanvas.width = this.image.width;
      backupCanvas.height = this.image.height;
      backupCtx.clearRect(0, 0, backupCanvas.width, backupCanvas.height);
      backupCtx.drawImage(
        this.maskCanvas,
        0,
        0,
        this.maskCanvas.width,
        this.maskCanvas.height,
        0,
        0,
        backupCanvas.width,
        backupCanvas.height
      );
      const backupData = backupCtx.getImageData(
        0,
        0,
        backupCanvas.width,
        backupCanvas.height
      );
      for (let i = 0; i < backupData.data.length; i += 4) {

        if (backupData.data[i + 3] == 255 && backupData.data[i] == 0){
          backupData.data[i + 3] = 0;
        }
        else if(backupData.data[i + 3] == 255 && backupData.data[i] == 255){
          backupData.data[i + 3] = 80;
        }
        else{
          backupData.data[i + 3] = 255;
          backupData.data[i] = 0;
          backupData.data[i + 1] = 0;
          backupData.data[i + 2] = 0;

        }


      }
      backupCtx.globalCompositeOperation = "source-over";
      backupCtx.putImageData(backupData, 0, 0);

      const coords = {
      };

      this.coords.forEach((item, index) => {
        const jsonItem = JSON.stringify(item);
        coords[index] = jsonItem;
      });

      const formData = new FormData();
      const filename = "clipspace-mask-" + performance.now() + ".png";
      const item = {
        filename,
        subfolder: "clipspace",
        type: "input"
      };
      if (ComfyApp.clipspace.images) ComfyApp.clipspace.images[0] = item;
      if (ComfyApp.clipspace.widgets) {
        const index = ComfyApp.clipspace.widgets.findIndex(
          (obj) => obj.name === "image"
        );
        if (index >= 0) ComfyApp.clipspace.widgets[index].value = item;
      }
      const dataURL = backupCanvas.toDataURL();

      const blob = dataURLToBlob(dataURL);
      let original_url = new URL(this.image.src);
      const original_ref = {
        filename: original_url.searchParams.get("filename")
      };
      let original_subfolder = original_url.searchParams.get("subfolder");
      if (original_subfolder) original_ref.subfolder = original_subfolder;
      let original_type = original_url.searchParams.get("type");
      if (original_type) original_ref.type = original_type;
      formData.append("image", blob, filename);
      formData.append("original_ref", JSON.stringify(original_ref));
      formData.append("type", "input");
      formData.append("subfolder", "clipspace");
      this.saveButton.innerText = "Saving...";
      this.saveButton.disabled = true;
      await uploadMask(item, formData);
      ComfyApp.onClipspaceEditorSave();
      const samData = new FormData();
      const numItems = this.coords.length;

      samData.append('nums', numItems);
      samData.append('coords', JSON.stringify(coords));
      samData.append('mode', (this.mode === "point") ? 1 : 0);
      samData.append('filename', filename);
      await uploadSamPrompt(samData)
      this.close();
    }
    addHistory(data) {
        this.history.push({
          'data': this.maskCtx.getImageData(0, 0, this.maskCanvas.width, this.maskCanvas.height)
        });
    }
    add_coords(){
      if(this.mode === "point"){
        this.coords.push({
          "startx": this.startx,
          "starty": this.starty,
          "pointType": ((this.brush_color_mode === "remain") ? 1 : 0)
        });
      }
      else{
        this.coords.push({
          "startx": this.startx,
          "starty": this.starty,
          "endx": this.endx,
          "endy": this.endy
        });
      }
    }

    showLastHistory() {
      if(this.history.length > 0){
          this.maskCtx.putImageData(this.history[this.history.length - 1]['data'], 0, 0)
      }
    }
    undo() {
      if(this.history.length > 0){
        this.history.pop();
      }
      if(this.coords.length > 0){
        this.coords.pop();
      }
    }

    resetHistory() {
      while (this.history.length > 0) {
        this.history.pop();
      }
      while (this.coords.length > 0) {
        this.coords.pop();
      }
    }

  }

export function sam_edit() {
    const dlg = SAMEditorDialog.getInstance();
      if (!dlg.isOpened()) {
        dlg.show();
      }
}
