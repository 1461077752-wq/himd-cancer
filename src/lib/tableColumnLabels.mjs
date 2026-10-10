// 窄屏表格竖排时，每个 td 要带上自己所在列的表头文字（见 global.css 的媒体查询）。
// Sätteri 的 hast 插件：只处理 Markdown 表格，把 thead 第一行的列名写进 tbody 单元格的 data-label。
function elementChildren(node) {
  return (node.children || []).filter((child) => child.type === 'element');
}

function firstByName(node, tagName) {
  return elementChildren(node).find((child) => child.tagName === tagName);
}

export const tableColumnLabels = {
  name: 'table-column-labels',
  element: {
    filter: ['table'],
    visit(node, ctx) {
      const thead = firstByName(node, 'thead');
      const tbody = firstByName(node, 'tbody');
      if (!thead || !tbody) return;
      const headerRow = elementChildren(thead)[0];
      if (!headerRow) return;
      const labels = elementChildren(headerRow).map((cell) => ctx.textContent(cell).trim());
      for (const row of elementChildren(tbody)) {
        elementChildren(row).forEach((cell, index) => {
          const label = labels[index];
          if (label) ctx.setProperty(cell, 'data-label', label);
        });
      }
    },
  },
};
