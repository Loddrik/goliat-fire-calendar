export function digest(buffer: ArrayBuffer): Promise<string>;
export function readVerifiedDocument(response: Response, expectedHash: string): Promise<import('./ObservedHistory').ObservedDoc>;
