export function validateCatalog(catalog) {
  if (!Array.isArray(catalog) || !catalog.length) return false;
  const ids = new Set();
  for (const tab of catalog) {
    if (!tab || !tab.id || !tab.name || ids.has(tab.id) || !Array.isArray(tab.operations) || !tab.operations.length) return false;
    ids.add(tab.id);
    const opIds = new Set();
    for (const op of tab.operations) {
      if (!op.id || !op.label || opIds.has(op.id) || !Array.isArray(op.fields) || !op.fields.length) return false;
      opIds.add(op.id);
      if (op.fields.some(f => !f.key || !f.label)) return false;
    }
  }
  return true;
}
export function findOperation(catalog, tab, op) {
  return (catalog.find(x=>x.id===tab)?.operations || []).find(x=>x.id===op) || null;
}
export function defaultsFor(catalog, tab, op) {
  return Object.fromEntries((findOperation(catalog,tab,op)?.fields || []).map(f=>[f.key, f.default ?? '']));
}
export function formatHistoryEntry(item) {
  return `${item.tab} / ${item.operation}: ${Object.values(item.values||{}).join('; ')} → ${item.result?.text ?? ''}`;
}
