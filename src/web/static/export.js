(function () {
  'use strict';

  function nowStamp() {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    return (
      d.getFullYear() +
      '-' +
      pad(d.getMonth() + 1) +
      '-' +
      pad(d.getDate()) +
      '_' +
      pad(d.getHours()) +
      pad(d.getMinutes()) +
      pad(d.getSeconds())
    );
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function svgToPngDataUrl(svgEl, scale) {
    return new Promise((resolve, reject) => {
      if (!svgEl) {
        reject(new Error('No SVG element found.'));
        return;
      }

      const bbox = svgEl.getBBox();
      const width = Math.ceil(bbox.width);
      const height = Math.ceil(bbox.height);
      if (!width || !height) {
        reject(new Error('SVG has zero width/height.'));
        return;
      }

      const cloned = svgEl.cloneNode(true);
      cloned.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      cloned.setAttribute('width', String(width));
      cloned.setAttribute('height', String(height));
      cloned.setAttribute('viewBox', `0 0 ${width} ${height}`);

      const serialized = new XMLSerializer().serializeToString(cloned);
      const svgBlob = new Blob([serialized], {
        type: 'image/svg+xml;charset=utf-8',
      });
      const svgUrl = URL.createObjectURL(svgBlob);

      const img = new Image();
      img.onload = () => {
        try {
          const canvas = document.createElement('canvas');
          canvas.width = Math.round(width * scale);
          canvas.height = Math.round(height * scale);
          const ctx = canvas.getContext('2d');
          ctx.setTransform(scale, 0, 0, scale, 0, 0);
          ctx.fillStyle = '#FFFFFF';
          ctx.fillRect(0, 0, width, height);
          ctx.drawImage(img, 0, 0);
          URL.revokeObjectURL(svgUrl);
          resolve(canvas.toDataURL('image/png'));
        } catch (err) {
          URL.revokeObjectURL(svgUrl);
          reject(err);
        }
      };
      img.onerror = (err) => {
        URL.revokeObjectURL(svgUrl);
        reject(err);
      };
      img.src = svgUrl;
    });
  }

  function mount() {
    const btn = document.getElementById('download-panel');
    if (!btn) {
      return;
    }

    btn.addEventListener('click', async () => {
      const panelId = document.getElementById('panel-select')?.value || '';
      const scale = parseFloat(document.getElementById('scale-select')?.value || '2');
      if (!panelId) {
        alert('Select a panel first.');
        return;
      }

      const panel = document.getElementById(panelId);
      const svg = panel ? panel.querySelector('svg') : null;
      try {
        const dataUrl = await svgToPngDataUrl(svg, isFinite(scale) ? scale : 2);
        const res = await fetch(dataUrl);
        const blob = await res.blob();
        downloadBlob(blob, `reposcape_${panelId}_${nowStamp()}@${scale}x.png`);
      } catch (err) {
        console.error(err);
        alert(`Export failed: ${err.message || err}`);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', mount);
})();
