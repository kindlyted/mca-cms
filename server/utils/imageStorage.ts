import { join } from 'path'

export function getDataAssetsDir(dataDir?: string): string {
  return join(dataDir || join(process.cwd(), 'data'), 'assets')
}
