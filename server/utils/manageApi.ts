import { existsSync, mkdirSync, writeFileSync, unlinkSync, readdirSync } from 'fs'
import { join } from 'path'
import { getDataRoot } from './localizedData'
import { getEntityConfig } from './contentApi'

// 返回实体可能的目录列表（product 支持分类子目录）
function getEntityDirs(type: string, lang: string, category?: string): string[] {
  const config = getEntityConfig(type)
  const dataRoot = getDataRoot()
  const baseDir = join(dataRoot, config.dataDir)

  if (config.categorySubdirs) {
    // 保存时按 meta.category 定位；删除时扫描所有分类
    if (category) {
      return [join(baseDir, category, lang)]
    }
    if (!existsSync(baseDir)) return []
    return readdirSync(baseDir, { withFileTypes: true })
      .filter(e => e.isDirectory())
      .map(e => join(baseDir, e.name, lang))
  }

  return [join(baseDir, lang)]
}

export function saveEntity(type: string, lang: string, data: any): { success: boolean; message: string; filePath?: string } {
  try {
    const config = getEntityConfig(type)
    const dataRoot = getDataRoot()
    const category = config.categorySubdirs ? (data.meta?.category || 'general') : undefined
    const entityDir = getEntityDirs(type, lang, category)[0]

    const id = data.meta?.id
    if (!id) {
      return { success: false, message: 'Missing meta.id in entity data' }
    }

    if (!data.meta?.createdAt) {
      data.meta.createdAt = new Date().toISOString()
    }
    data.meta.updatedAt = new Date().toISOString()

    mkdirSync(entityDir, { recursive: true })
    const filePath = join(entityDir, `${id}.json`)
    writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')

    return { success: true, message: `${type} saved successfully`, filePath }
  } catch (error) {
    console.error(`Error saving ${type}:`, error)
    return { success: false, message: `Failed to save ${type}: ${error instanceof Error ? error.message : String(error)}` }
  }
}

export function deleteEntity(type: string, lang: string, id: string): { success: boolean; message: string } {
  try {
    const dirs = getEntityDirs(type, lang)
    let filePath: string | null = null
    for (const entityDir of dirs) {
      const candidate = join(entityDir, `${id}.json`)
      if (existsSync(candidate)) {
        filePath = candidate
        break
      }
    }

    if (!filePath) {
      return { success: false, message: `${type} not found: ${id}` }
    }

    unlinkSync(filePath)
    return { success: true, message: `${type} deleted successfully` }
  } catch (error) {
    console.error(`Error deleting ${type}:`, error)
    return { success: false, message: `Failed to delete ${type}: ${error instanceof Error ? error.message : String(error)}` }
  }
}
