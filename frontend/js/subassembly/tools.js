export const hideWidget = (node, widget_name) => {
  const widget = node.widgets.find(widget => widget.name === widget_name)
  if (!widget) {
    return
  }

  const originalComputeSize = widget.computeSize;
  const originalType = widget.type;

  widget.computeSize = () => [0, -4];
  widget.height = 0;
  widget.type = "hidden";
  widget.options = widget.options || {};
  widget.show = () => {
    widget.computeSize = originalComputeSize;
    widget.type = originalType;
    widget.height = undefined;
  };
}
