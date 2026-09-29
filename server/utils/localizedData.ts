import { existsSync, readdirSync, readFileSync } from 'fs'
import { join, relative, sep } from 'path'

export function getDataRoot() {
  const config = useRuntimeConfig()
  if (config.dataDir) {
    const normalized = config.dataDir.replace(/\\/g, '/')
    if (!existsSync(normalized)) {
      console.warn(`⚠️ [getDataRoot] dataDir does not exist: ${normalized}`)
      console.warn(`   Set NITRO_DATA_DIR env var on the server to the correct data path.`)
    }
    return normalized
  }
  // 默认使用项目根目录下的 data/
  const defaultDir = join(process.cwd(), 'data')
  if (!existsSync(defaultDir)) {
    console.warn(`⚠️ [getDataRoot] Default data dir does not exist: ${defaultDir}`)
    console.warn(`   Set NITRO_DATA_DIR env var on the server to the correct data path.`)
  }
  return defaultDir
}

export function getJsonFilesRecursive(dir: string): string[] {
  const entries = readdirSync(dir, { withFileTypes: true })
  const files: string[] = []

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)
    if (entry.isDirectory()) {
      files.push(...getJsonFilesRecursive(fullPath))
    } else if (entry.isFile() && entry.name.endsWith('.json')) {
      files.push(fullPath)
    }
  }

  return files
}

export function readJsonFile(filePath: string) {
  return JSON.parse(readFileSync(filePath, 'utf-8'))
}

/**
 * Resolve path following shared-data + translation architecture:
 *   1. Try {baseDir}/translations/{lang}/{id}.json  (translated version)
 *   2. Try {baseDir}/{lang}/{id}.json               (legacy locale folder)
 *   3. Try {baseDir}/{id}.json                       (legacy monolithic, fallback)
 */
export function resolveLocalizedJsonPath(baseDir: string, id: string, lang: string): string | null {
  // New architecture: translations/{lang}/{id}.json
  const translationPath = join(baseDir, 'translations', lang, `${id}.json`)
  if (existsSync(translationPath)) {
    return translationPath
  }

  // Legacy: {lang}/{id}.json (for blog, etc.)
  const localizedPath = join(baseDir, lang, `${id}.json`)
  if (existsSync(localizedPath)) {
    return localizedPath
  }

  // Fallback: root level
  const defaultPath = join(baseDir, `${id}.json`)
  if (existsSync(defaultPath)) {
    return defaultPath
  }

  return null
}

/**
 * Load and merge shared data + translation for a given entity.
 * 
 * Architecture pattern (from reactvisa-master/chinavisa/data):
 *   - Shared file:  {baseDir}/{id}.json        → language-agnostic structural data
 *   - Translation:  {baseDir}/translations/{lang}/{id}.json → all user-facing text
 * 
 * Returns deep-merged object where translation overrides shared fields.
 */
export function loadMergedLocalizedJson(baseDir: string, id: string, lang: string): Record<string, any> | null {
  // 1. Load shared (base) data
  const sharedPath = join(baseDir, `${id}.json`)
  if (!existsSync(sharedPath)) {
    return null
  }
  const shared = readJsonFile(sharedPath)

  // 2. Load translation overlay
  const transPath = join(baseDir, 'translations', lang, `${id}.json`)
  if (!existsSync(transPath)) {
    // No translation for this locale; try 'en' as fallback
    const enPath = join(baseDir, 'translations', 'en', `${id}.json`)
    if (existsSync(enPath)) {
      const translation = readJsonFile(enPath)
      return deepMerge(shared, translation)
    }
    // No translations at all, return shared data as-is
    return shared
  }

  const translation = readJsonFile(transPath)
  return deepMerge(shared, translation)
}

/**
 * Deep merge two objects. `override` values take precedence over `base`.
 * Arrays are replaced (not concatenated). Nested objects are merged recursively.
 */
function deepMerge(base: Record<string, any>, override: Record<string, any>): Record<string, any> {
  const result = { ...base }

  for (const key of Object.keys(override)) {
    if (
      override[key] !== null &&
      typeof override[key] === 'object' &&
      !Array.isArray(override[key]) &&
      base[key] !== null &&
      typeof base[key] === 'object' &&
      !Array.isArray(base[key])
    ) {
      result[key] = deepMerge(base[key], override[key])
    } else {
      result[key] = override[key]
    }
  }

  return result
}

function isLocaleFolderName(segment: string) {
  const supportedLocales = ['en', 'fr', 'de']
  return supportedLocales.includes(segment)
}

export function getLocalizedJsonFiles(baseDir: string, lang: string): string[] {
  if (!existsSync(baseDir)) {
    return []
  }

  const localizedDir = join(baseDir, lang)
  if (existsSync(localizedDir)) {
    return getJsonFilesRecursive(localizedDir)
  }

  const files = getJsonFilesRecursive(baseDir)

  if (lang === 'en') {
    return files.filter(filePath => {
      const relativePath = relative(baseDir, filePath)
      const firstSegment = relativePath.split(sep)[0]
      if (isLocaleFolderName(firstSegment)) {
        return false
      }
      try {
        const data = readJsonFile(filePath)
        return (data.meta?.language || 'en') === 'en'
      } catch {
        return false
      }
    })
  }

  const localizedFiles = files.filter(filePath => {
    try {
      const data = readJsonFile(filePath)
      return (data.meta?.language || 'en') === lang
    } catch {
      return false
    }
  })

  if (localizedFiles.length > 0) {
    return localizedFiles
  }

  return files.filter(filePath => {
    try {
      const data = readJsonFile(filePath)
      return (data.meta?.language || 'en') === 'en'
    } catch {
      return false
    }
  })
}
