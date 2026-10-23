/* Browser-side persistence boundary for the versioned mathematical graph.
 * Data is JSON-only. The Python workspace remains the authoritative validator:
 * this module rejects obvious corruption before attempting replay.
 */
export const WORKSPACE_STORAGE_KEY = 'calculator2.workspace.v1';
const MAX_CHARS = 75000;
const MAX_STEPS = 64;
const FIELDS = {
  define: new Set(['command','id','kind','coordinates','metric','expression','components','matrix']),
  apply: new Set(['command','id','operation','source','other','variable','order','point',
                  'lower','upper','expression','normals','independent','coordinates','mapping']),
};
const plain = value => value !== null && typeof value === 'object' &&
  !Array.isArray(value) && Object.getPrototypeOf(value) === Object.prototype;

export function validWorkspaceSnapshot(value) {
  if (!plain(value) || Object.keys(value).sort().join(',') !== 'format,steps,version' ||
      value.format !== 'calculator2.workspace' || value.version !== 1 ||
      !Array.isArray(value.steps) || value.steps.length > MAX_STEPS) return false;
  return value.steps.every(step => {
    if (!plain(step) || !(step.command in FIELDS) ||
        typeof step.id !== 'string' || !/^[a-z][a-z0-9_]{0,31}$/.test(step.id)) return false;
    return Object.keys(step).every(key => FIELDS[step.command].has(key));
  });
}

export function readWorkspaceSnapshot(storage) {
  try {
    const data = storage.getItem(WORKSPACE_STORAGE_KEY);
    if (typeof data !== 'string' || data.length > MAX_CHARS) return null;
    const parsed = JSON.parse(data);
    return validWorkspaceSnapshot(parsed) ? parsed : null;
  } catch {
    return null; // missing, disabled, unavailable or corrupt storage
  }
}

export function writeWorkspaceSnapshot(storage, snapshot) {
  if (!validWorkspaceSnapshot(snapshot)) throw new Error('Invalid workspace snapshot.');
  const json = JSON.stringify(snapshot);
  if (json.length > MAX_CHARS) throw new Error('Workspace snapshot exceeds storage size limit.');
  storage.setItem(WORKSPACE_STORAGE_KEY, json);
}

export function clearWorkspaceSnapshot(storage) {
  storage.removeItem(WORKSPACE_STORAGE_KEY);
}
