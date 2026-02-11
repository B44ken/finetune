const scrapeConvoDiscord = () => {
    const fmtName = (n: string) => n.startsWith('b4') ? 'b4444' : n.replace(/[^a-z0-9]+/gi, "-")
    const textbox = getTextbox()?.textContent?.split('\u200b')?.[0]?.trim()

    const msgs = [...document.querySelectorAll('[id^="chat-messages"]')].map(m => {
        const nameEl = m.querySelector('[id^="message-username"] [role=button]') as HTMLDivElement | null
        const contentEl = m.querySelector('[id^="message-content"]') as HTMLDivElement | null
        const name = fmtName(nameEl?.innerText ?? '')
        return { name, role: name == 'b4444' ? 'assistant' : 'user', content: contentEl?.innerText ?? '' }
    }).filter(x => x != null).slice(-7)

    return '<|im_start|>system\ncontinue this discord conversation (you are b4444) (there may be a partial message already, if so, continue typing from that point onwards, completing the message, withourt retyping the first part) (never include "b4444:" or attempt to respond as any other user, just continue the conversation) /nothink <|im_end|>\n' +
        msgs.map(m => `<|im_start|>${m.role}\n${m.name}: ${m.content}<|im_end|>`).join('\n') +
        (textbox ? `\n1assistant\nb4444: ${textbox}` : '')
}


const ollamaFetch = async (prompt: string, model = 'discordqwen14b') =>
    fetch('http://localhost:11434/api/generate', { method: 'POST', body: JSON.stringify({ model, prompt }) }).then(async resp => {
        const reader = resp.body!.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        while (true) reader.read().then(r => {
            if (r.done) return
            buffer += JSON.parse(decoder.decode(r.value)).response
            suggestDiscord(buffer)
        })
    })

addEventListener('keydown', (ev) => {
    if (ev.key == 'Tab') {
        if (ev.shiftKey) acceptSuggestion()
        else ollamaFetch(scrapeConvoDiscord())
        ev.preventDefault()
    }
})

const suggestDiscord = (text: string) => {
    selectFromMarker()
    dispatchInput('\u200b' + text.replaceAll('\n', ' '))
    setTimeout(moveBeforeMarker, 0)
}

const getTextbox = () => document.querySelector('[role="textbox"]') as HTMLDivElement | null

const dispatchInput = (data: string, inputType = 'insertText', bubbles = true, cancelable = true) =>
    getTextbox()?.dispatchEvent(new InputEvent('beforeinput', { data, inputType, bubbles, cancelable }))

const collapseToEnd = () => {
    const sel = window.getSelection()!
    sel.selectAllChildren(getTextbox()!)
    sel.collapseToEnd()
}

const withMarker = (fn: (node: Text, idx: number) => void) => {
    const el = getTextbox()!
    el.focus()
    let node = null
    let walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT)
    while (node = walker.nextNode() as Text | null) {
        const idx = node.textContent!.indexOf('\u200b')
        if (idx !== -1) return fn(node, idx)
    }
}


const setRange = (node: Node, start: number, end?: number) => {
    const sel = window.getSelection()!
    const range = document.createRange()
    sel.removeAllRanges()
    range.setStart(node, start)
    end != null ? range.setEnd(node, end) : range.collapse(true)
    sel.addRange(range)
}

const selectFromMarker = () => withMarker((node, idx) => setRange(node, idx, node.textContent!.length))
const moveBeforeMarker = () => withMarker((node, idx) => setRange(node, idx))
const acceptSuggestion = () => withMarker((node, idx) => {
    setRange(node, idx, idx + 1)
    dispatchInput('')
    setTimeout(collapseToEnd, 0)
})