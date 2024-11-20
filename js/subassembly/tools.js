export const hideWidget = (node, widget_name) => {
  const widget = node.widgets.find(widget => widget.name === widget_name)
  if (!widget) {
    return
  }
  widget.computeSize = () => [0, 0]
  widget.height = 0
  widget.type = "hidden"

  widget.options = widget.options || {}
  setTimeout(() => {
    if (node.setSize) {
        node.computeSize();
        node.setSize(node.computeSize());
        node.graph?.setDirtyCanvas(true, true);
    }
    }, 0);
}
