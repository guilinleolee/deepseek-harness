"""Patcher P3-notes: add research note tools and domain updates."""
import io

WT = 'D:/dsh-wt-quant-p1/packages/quant/quant-research/'

def patch(path, old, new):
    fp = WT + path
    s = io.open(fp, encoding='utf-8').read()
    assert old in s, f'{path}: {old[:60]!r}'
    s = s.replace(old, new)
    io.open(fp, 'w', encoding='utf-8', newline='\n').write(s)
    print('patched', path)

# 1. domain spec: ResearchNoteId brand + schema + table
p = 'src/domain/spec.ts'
s = io.open(WT + p, encoding='utf-8').read()
if 'ResearchNoteId' not in s:
    s = s.replace(
        "export type OrderId = Branded<'OrderId'>",
        "export type OrderId = Branded<'OrderId'>\nexport type ResearchNoteId = Branded<'ResearchNoteId'>")
    s = s.replace(
        "/** One red-line denial record. */",
        """export const researchNoteSchema = z.object({
  id: z.string().min(1).transform(ResearchNoteId),
  title: z.string().min(1),
  body: z.string().min(1),
  symbol: z.string().min(1).optional(),
  tags: z.array(z.string().min(1)).refine(
    tags => new Set(tags).size === tags.length,
    { message: 'duplicate tag' },
  ),
  created_at: epochMs,
})
export type ResearchNote = z.infer<typeof researchNoteSchema>

/** One red-line denial record. */""")
    s = s.replace(
        "orders: domainTable<OrderId, Order>(orderSchema),\n  },",
        "orders: domainTable<OrderId, Order>(orderSchema),\n    research_notes: domainTable<ResearchNoteId, ResearchNote>(researchNoteSchema),\n  },")
    # Add constructor
    s = s.replace(
        "export const OrderId = (value: string): OrderId => value as OrderId",
        "export const OrderId = (value: string): OrderId => value as OrderId\n\n/** Brand a plain string as a research note id. */\nexport const ResearchNoteId = (value: string): ResearchNoteId => value as ResearchNoteId")
    io.open(WT + p, 'w', encoding='utf-8', newline='\n').write(s)
    print('domain spec updated')

# 2. index.ts exports
p = 'src/index.ts'
s = io.open(WT + p, encoding='utf-8').read()
s = s.replace(
    "} from './pet/service.ts'",
    "} from './pet/service.ts'\nexport {\n  deleteNote, exportNotesMarkdown, listNotes, renderNoteMarkdown, saveNote,\n} from './pet/notes.ts'\nexport type { NoteSaveInput } from './pet/notes.ts'\nexport type { ResearchNote } from './domain/spec.ts'")
s = s.replace(
    "  executeRebalanceTool, factorICTool, getKlineTool, registerQuantTools, runBacktestTool,\n  stressTestTool,\n} from './tools.ts'",
    "  executeRebalanceTool, exportReportTool, factorICTool, getKlineTool, listNotesTool,\n  registerQuantTools, runBacktestTool, saveNoteTool, stressTestTool,\n} from './tools.ts'")
s = s.replace(
    "  AccountId, OrderId, accountSchema, complianceDenialSchema, orderSchema,\n  quantResearchDomainSpec,\n} from './domain/spec.ts'",
    "  AccountId, OrderId, ResearchNoteId, accountSchema, complianceDenialSchema, orderSchema,\n  quantResearchDomainSpec, researchNoteSchema,\n} from './domain/spec.ts'")
io.open(WT + p, 'w', encoding='utf-8', newline='\n').write(s)
print('index.ts exports updated')
print('patcher done')
