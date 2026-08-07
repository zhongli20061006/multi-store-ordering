import { describe, expect, it } from 'vitest'
import { buildAuditFilename, buildExportFilename } from '../csv-download'

describe('buildExportFilename', () => {
  it('生成 门店-订单-日期时间.csv', () => {
    const date = new Date(2026, 7, 6, 15, 30)
    expect(buildExportFilename('中山路店', date)).toBe('中山路店-订单-20260806-1530.csv')
  })

  it('生成 门店-审计-日期时间.csv', () => {
    const date = new Date(2026, 7, 6, 15, 30)
    expect(buildAuditFilename('中山路店', date)).toBe('中山路店-审计-20260806-1530.csv')
  })
})
