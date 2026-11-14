export async function digest(buffer) {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', buffer)))
    .map(value => value.toString(16).padStart(2, '0')).join('');
}

export async function readVerifiedDocument(response, expectedHash) {
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const buffer = await response.arrayBuffer();
  if (await digest(buffer) !== expectedHash) throw new Error('SHA-256 mismatch');
  const doc = JSON.parse(new TextDecoder().decode(buffer));
  if (doc.schema_version !== 1 || doc.product !== 'observed-platform-history' ||
      doc.unit !== 'cell_days_per_platform' || doc.harmonization !== 'none') {
    throw new Error('Unexpected observed data contract');
  }
  return doc;
}
